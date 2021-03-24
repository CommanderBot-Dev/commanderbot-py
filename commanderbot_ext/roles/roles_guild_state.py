import asyncio
from dataclasses import dataclass
from typing import List, Optional, Tuple, cast

from discord import Member, Message, Permissions, Reaction, Role

from commanderbot_ext._lib.cog_guild_state import CogGuildState
from commanderbot_ext._lib.types import GuildContext, GuildRole, RoleID
from commanderbot_ext.roles.roles_store import RolesRoleEntry, RolesStore

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


RoleEntryPair = Tuple[GuildRole, RolesRoleEntry]


@dataclass
class RolesGuildState(CogGuildState):
    store: RolesStore

    def _resolve_role(self, role_id: RoleID) -> Optional[GuildRole]:
        # Attempt to resolve the role from the given ID.
        role = self.guild.get_role(role_id)
        # If the role resolves correctly, return it.
        if isinstance(role, Role):
            return cast(GuildRole, role)
        # Otherwise skip it, but log so the role can be fixed.
        self.log.exception(f"Failed to resolve role ID: {role_id}")

    def _sort_role_pairs(self, role_pairs: List[RoleEntryPair]) -> List[RoleEntryPair]:
        # Sort by stringified role name.
        return sorted(role_pairs, key=lambda role_pair: str(role_pair[0]))

    def _get_all_role_pairs(self) -> List[RoleEntryPair]:
        # Flatten the full list of role entry pairs.
        role_pairs: List[RoleEntryPair] = []
        async for role_id, role_entry in self.store.iter_role_entries(self.guild):
            # If the role was resolved, add it to the list.
            if role := self._resolve_role(role_id):
                role_pairs.append((role, role_entry))
        # Sort and return.
        return self._sort_role_pairs(role_pairs)

    def _get_relevant_role_for(
        self, role_id: int, role_entry: RolesRoleEntry, member: Member
    ) -> Optional[GuildRole]:
        # If the role didn't resolve, it certainly isn't relevant.
        if role := self._resolve_role(role_id):
            # A role is relevant to the user if:
            # 1. it's joinable; or
            # 2. it's leavable and present on the user.
            if role_entry.joinable or (role_entry.leavable and role in member.roles):
                return role

    def _get_relevant_role_pairs(self, member: Member) -> List[RoleEntryPair]:
        # Build a list of relevant role entry pairs.
        role_pairs: List[RoleEntryPair] = []
        async for role_id, role_entry in self.store.iter_role_entries(self.guild):
            # If the role is relevant to the user, add it to the list.
            if role := self._get_relevant_role_for(role_id, role_entry, member):
                role_pairs.append((role, role_entry))
        # Sort and return.
        return self._sort_role_pairs(role_pairs)

    async def _confirm_register_unsafe_role(
        self, ctx: GuildContext, role: GuildRole, unsafe_perms: Permissions
    ) -> bool:
        # Build and send a confirmation message.
        unsafe_perms_str = "\n".join(
            f"- `{pname}`" for pname, pvalue in unsafe_perms if pvalue
        )
        message_str = "\n".join(
            [
                f"`{role}` contains potentially unsafe permissions:",
                unsafe_perms_str,
                f"Do you want to register `{role}` anyway?",
            ]
        )
        conf_message: Message = await ctx.reply(message_str)

        # Have the bot pre-fill the possible choices for convenience.
        await conf_message.add_reaction(REACTION_YES)
        await conf_message.add_reaction(REACTION_NO)

        # Define a callback to listen for a reaction to the confirmation message.
        def reacted_to_conf_message(reaction: Reaction, user: Member):
            return (
                reaction.message == conf_message
                and user == ctx.author
                and str(reaction.emoji) in (REACTION_YES, REACTION_NO)
            )

        # Attempt to wait for a reaction to the confirmation message.
        try:
            conf_reaction, conf_user = await self.bot.wait_for(
                "reaction_add", timeout=60.0, check=reacted_to_conf_message
            )
        # If an appropriate reaction is not received soon enough, assume "no."
        except asyncio.TimeoutError:
            pass
        # Otherwise, check which reaction was applied.
        else:
            assert isinstance(conf_reaction, Reaction)
            if str(conf_reaction.emoji) == REACTION_YES:
                await conf_message.remove_reaction(REACTION_NO, self.bot.user)
                return True
        # If we get this far, the answer is "no."
        await conf_message.remove_reaction(REACTION_YES, self.bot.user)
        return False

    def _get_unsafe_role_perms(self, role: GuildRole) -> Optional[Permissions]:
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

    async def _should_register_role(self, ctx: GuildContext, role: GuildRole) -> bool:
        # If the role contains unsafe permissions, ask for confirmation.
        if unsafe_perms := self._get_unsafe_role_perms(role):
            return await self._confirm_register_unsafe_role(ctx, role, unsafe_perms)
        # Otherwise, the role can be registered right away.
        return True

    def _stringify_role_pairs(
        self, ctx: GuildContext, role_pairs: List[RoleEntryPair]
    ) -> str:
        lines = []
        for role, role_entry in role_pairs:
            # Build the role title line.
            role_title_parts = [f"`{role}`"]
            if not role_entry.joinable:
                role_title_parts.append(" (not joinable)")
            if not role_entry.leavable:
                role_title_parts.append(" (not leavable)")
            role_title_line = "".join(role_title_parts)
            lines.append(f"- {role_title_line}")
        return "\n".join(lines)

    async def register_role(
        self, ctx: GuildContext, role: GuildRole, joinable: bool, leavable: bool
    ):
        # Check whether this is a role that should be registered.
        if await self._should_register_role(ctx, role):
            role_entry = await self.store.add_role(
                role, joinable=joinable, leavable=leavable
            )
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
        else:
            await ctx.send(f"❌ `{role}` has **not** been registered.")

    async def deregister_role(self, ctx: GuildContext, role: GuildRole):
        # Any role can always be deregistered.
        if await self.store.remove_role(role):
            await ctx.send(f"✅ `{role}` has been deregistered.")
        else:
            await ctx.send(f"🤷 `{role}` is not registered.")

    async def add_role_to_members(
        self, ctx: GuildContext, role: GuildRole, members: List[Member]
    ):
        # The acting user ought to be a [Member].
        acting_user = ctx.author
        assert isinstance(acting_user, Member)
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
        if role_pairs := self._get_all_role_pairs():
            role_pairs_str = self._stringify_role_pairs(ctx, role_pairs)
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
        if role_pairs := self._get_relevant_role_pairs(member):
            role_pairs_str = self._stringify_role_pairs(ctx, role_pairs)
            await ctx.reply(
                f"There are {len(role_pairs)} roles available to you:\n{role_pairs_str}"
            )
        else:
            await ctx.reply(f"🤷 There are no roles available to you.")

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
            await ctx.send(f"🤷 `{role}` is not registered.")

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
            await ctx.send(f"🤷 `{role}` is not registered.")
