from dataclasses import dataclass
from typing import List, Optional, cast

from discord import Member, Message, Permissions, Role

from commanderbot_ext.ext.roles.roles_store import (
    RoleEntry,
    RoleEntryPair,
    RolesException,
    RolesStore,
)
from commanderbot_ext.lib import CogGuildState, GuildContext, GuildRole, RoleID
from commanderbot_ext.lib.dialogs import ConfirmationResult, confirm_with_reaction

REACTION_YES = "✅"
REACTION_NO = "❌"

SAFE_PERMS = Permissions.none()
# general
SAFE_PERMS.read_messages = True
# membership
SAFE_PERMS.change_nickname = True
# text channel
SAFE_PERMS.send_messages = True
SAFE_PERMS.embed_links = True
SAFE_PERMS.attach_files = True
SAFE_PERMS.add_reactions = True
SAFE_PERMS.external_emojis = True
SAFE_PERMS.read_message_history = True
# voice channel
SAFE_PERMS.connect = True
SAFE_PERMS.speak = True
SAFE_PERMS.stream = True
SAFE_PERMS.use_voice_activation = True


@dataclass
class RolesGuildState(CogGuildState):
    """
    Encapsulates the state and logic of the roles cog, at the guild level.

    Attributes
    -----------
    store
        The store used to interface with persistent data in a database-agnostic way.
    """

    store: RolesStore

    def _sort_role_pairs(self, role_pairs: List[RoleEntryPair]) -> List[RoleEntryPair]:
        # Sort by stringified role name.
        return sorted(role_pairs, key=lambda role_pair: str(role_pair[0]))

    def _stringify_role_pairs(self, role_pairs: List[RoleEntryPair]) -> str:
        lines = []
        for role, role_entry in role_pairs:
            # Start with the role's actual name.
            role_line_parts = [f"`{role}`"]
            # Mention that it's not joinable, if applicable.
            if not role_entry.joinable:
                role_line_parts.append(" (not joinable)")
            # Mention that it's not leavable, if applicable.
            if not role_entry.leavable:
                role_line_parts.append(" (not leavable)")
            # Add its description, if any.
            if role_entry.description:
                role_line_parts.append(f": {role_entry.description}")
            role_line = "".join(role_line_parts)
            lines.append(f"- {role_line}")
        return "\n".join(lines)

    async def _resolve_role(self, role_id: RoleID) -> Optional[GuildRole]:
        # Attempt to resolve the role from the given ID.
        role = self.guild.get_role(role_id)
        # If the role resolves correctly, return it.
        if isinstance(role, Role):
            return cast(GuildRole, role)
        # Otherwise skip it, but log so the role can be fixed.
        self.log.exception(f"Failed to resolve role ID: {role_id}")

    async def _get_all_role_pairs(self) -> List[RoleEntryPair]:
        # Flatten the full list of role entry pairs.
        role_pairs: List[RoleEntryPair] = []
        async for role_id, role_entry in self.store.iter_role_entries(self.guild):
            # If the role was resolved, add it to the list.
            if role := await self._resolve_role(role_id):
                role_pairs.append((role, role_entry))
        # Sort and return.
        return self._sort_role_pairs(role_pairs)

    async def _get_relevant_role_for(
        self, role_id: int, role_entry: RoleEntry, member: Member
    ) -> Optional[GuildRole]:
        # If the role didn't resolve, it certainly isn't relevant.
        if role := await self._resolve_role(role_id):
            # A role is relevant to the user if:
            # 1. it's joinable; or
            # 2. it's leavable and present on the user.
            if role_entry.joinable or (role_entry.leavable and role in member.roles):
                return role

    async def _get_relevant_role_pairs(self, member: Member) -> List[RoleEntryPair]:
        # Build a list of relevant role entry pairs.
        role_pairs: List[RoleEntryPair] = []
        async for role_id, role_entry in self.store.iter_role_entries(self.guild):
            # If the role is relevant to the user, add it to the list.
            if role := await self._get_relevant_role_for(role_id, role_entry, member):
                role_pairs.append((role, role_entry))
        # Sort and return.
        return self._sort_role_pairs(role_pairs)

    async def _get_unsafe_role_perms(self, role: GuildRole) -> Optional[Permissions]:
        # Start with an empty set of unsafe permissions.
        unsafe_perms = Permissions.none()
        # Collect all of the enabled permissions.
        unsafe_pnames = [pname for (pname, pvalue) in role.permissions if pvalue]
        for pname in unsafe_pnames:
            # If this permission is not safe, add it to the set of unsafe permissions.
            if not getattr(SAFE_PERMS, pname):
                setattr(unsafe_perms, pname, True)
        # Only return a [Permissions] object if there's actually something in it.
        if unsafe_perms != Permissions.none():
            return unsafe_perms

    async def _should_register_role(
        self, ctx: GuildContext, role: GuildRole
    ) -> ConfirmationResult:
        # If the role contains unsafe permissions, ask for confirmation.
        if unsafe_perms := await self._get_unsafe_role_perms(role):
            unsafe_perms_str = "\n".join(
                f"- `{pname}`" for pname, pvalue in unsafe_perms if pvalue
            )
            conf_content = "\n".join(
                [
                    f"`{role}` contains potentially unsafe permissions:",
                    unsafe_perms_str,
                    f"Do you want to register `{role}` anyway?",
                ]
            )
            return await confirm_with_reaction(self.bot, ctx, conf_content)
        # Otherwise, the role can be registered right away.
        return ConfirmationResult.YES

    async def register_role(
        self,
        ctx: GuildContext,
        role: GuildRole,
        joinable: bool,
        leavable: bool,
        description: Optional[str],
    ):
        # Wrap this in case of multiple confirmations.
        try:
            # Check whether this is a role that should be registered. If the role
            # contains unsafe permissions, this will also ask for confirmation.
            conf = await self._should_register_role(ctx, role)
            # If the answer was yes...
            if conf == ConfirmationResult.YES:
                # Attempt to register the role.
                role_entry = await self.store.register_role(
                    role,
                    joinable=joinable,
                    leavable=leavable,
                    description=description,
                )
                # Send a response that includes some confirmation about the flags.
                if role_entry.joinable and role_entry.leavable:
                    await ctx.send(f"✅ `{role}` has been registered as opt-in/opt-out.")
                elif role_entry.joinable:
                    await ctx.send(
                        f"✅ `{role}` has been registered as **opt-in only** (not leavable)."
                    )
                elif role_entry.leavable:
                    await ctx.send(
                        f"✅ `{role}` has been registered as **opt-out only** (not joinable)."
                    )
                else:
                    await ctx.send(
                        f"✅ `{role}` has been registered, but is **neither opt-in nor opt-out**."
                    )
            # If the answer was no, send a response.
            if conf == ConfirmationResult.NO:
                await ctx.send(f"❌ `{role}` has **not** been registered.")
            # If no answer was provided, don't do anything.
        # If a known error occurred, send a response.
        except RolesException as ex:
            await ex.respond(ctx)

    async def deregister_role(self, ctx: GuildContext, role: GuildRole):
        try:
            await self.store.deregister_role(role)
            await ctx.send(f"✅ `{role}` has been deregistered.")
        except RolesException as ex:
            await ex.respond(ctx)

    async def add_role_to_members(
        self, ctx: GuildContext, role: GuildRole, members: List[Member]
    ):
        # The acting user ought to be a [Member].
        acting_user = ctx.author
        assert isinstance(acting_user, Member)
        # Make sure we actually have some members.
        if not members:
            await ctx.reply("🤔 You didn't provide any members.")
            return
        # Add the role to each member who does not already have it.
        added_members: List[Member] = []
        for member in members:
            if role not in member.roles:
                await member.add_roles(role, reason=f"{acting_user} added role to user")
                added_members.append(member)
        # Send a response with edit-mentions.
        if added_members:
            members_str = " ".join(f"{member.mention}" for member in added_members)
            message: Message = await ctx.reply("\\🤖")
            await message.edit(content=f"✅ Added role `{role}` to: {members_str}")
        else:
            await ctx.reply("🤷 All of those users already have that role.")

    async def remove_role_from_members(
        self, ctx: GuildContext, role: GuildRole, members: List[Member]
    ):
        # The acting user ought to be a [Member].
        acting_user = ctx.author
        assert isinstance(acting_user, Member)
        # Make sure we actually have some members.
        if not members:
            await ctx.reply("🤔 You didn't provide any members.")
            return
        # Remove the role from each member who has it.
        removed_members: List[Member] = []
        for member in members:
            if role in member.roles:
                await member.remove_roles(
                    role, reason=f"{acting_user} removed role from user"
                )
                removed_members.append(member)
        # Send a response with edit-mentions.
        if removed_members:
            members_str = " ".join(f"{member.mention}" for member in removed_members)
            message: Message = await ctx.reply("`🤖`")
            await message.edit(content=f"✅ Removed role `{role}` from: {members_str}")
        else:
            await ctx.reply("🤷 None of those users have that role.")

    async def show_all_roles(self, ctx: GuildContext):
        if role_pairs := await self._get_all_role_pairs():
            role_pairs_str = self._stringify_role_pairs(role_pairs)
            await ctx.send(
                f"There are {len(role_pairs)} roles registered:\n{role_pairs_str}"
            )
        else:
            await ctx.send(f"🤷 There are no roles registered.")

    async def show_relevant_roles(self, ctx: GuildContext):
        # We ought to have a [Member].
        member = ctx.author
        assert isinstance(member, Member)
        # List only roles that are relevant to this user.
        if role_pairs := await self._get_relevant_role_pairs(member):
            role_pairs_str = self._stringify_role_pairs(role_pairs)
            await ctx.reply(
                f"There are {len(role_pairs)} roles relevant to you:\n{role_pairs_str}"
            )
        else:
            await ctx.reply(f"🤷 There are no roles relevant to you.")

    async def join_role(self, ctx: GuildContext, role: GuildRole):
        # We ought to have a [Member].
        member = ctx.author
        assert isinstance(member, Member)
        # Only consider roles that have actually been registered.
        if role_entry := await self.store.get_role_entry(role):
            # First, check if they already have the role.
            if role in member.roles:
                await ctx.reply(f"🤔 You're already in `{role}`.")
            # Then, check if the role is indeed joinable.
            elif role_entry.joinable:
                await member.add_roles(role, reason="User opted-in to role")
                await ctx.reply(f"✅ You have joined `{role}`.")
            # Otherwise, they can't join it.
            else:
                await ctx.reply(f"❌ You cannot join `{role}`.")
        else:
            await ctx.reply(f"🤷 `{role}` is not registered.")

    async def leave_role(self, ctx: GuildContext, role: GuildRole):
        # We ought to have a [Member].
        member = ctx.author
        assert isinstance(member, Member)
        # Only consider roles that have actually been registered.
        if role_entry := await self.store.get_role_entry(role):
            # First, check if they don't already have the role.
            if role not in member.roles:
                await ctx.reply(f"🤔 You aren't in `{role}`.")
            # Then, check if the role is indeed leavable.
            elif role_entry.leavable:
                await member.remove_roles(role, reason="User opted-out of role")
                await ctx.reply(f"✅ You have left `{role}`.")
            # Otherwise, they can't leave it.
            else:
                await ctx.reply(f"❌ You cannot leave `{role}`.")
        else:
            await ctx.reply(f"🤷 `{role}` is not registered.")
