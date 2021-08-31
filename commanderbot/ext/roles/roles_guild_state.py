from dataclasses import dataclass
from typing import List, Optional, Type

from discord import AllowedMentions, Member, Message, Permissions, Role

from commanderbot.ext.roles.roles_result import (
    AddableRolesResult,
    JoinableRolesResult,
    LeavableRolesResult,
    RemovableRolesResult,
    RolesResult,
)
from commanderbot.ext.roles.roles_store import RoleEntry, RoleEntryPair, RolesStore
from commanderbot.lib import CogGuildState, GuildContext, MemberContext, RoleID, RoleSet
from commanderbot.lib.dialogs import ConfirmationResult, confirm_with_reaction

SAFE_PERMS = Permissions.none()
# general
SAFE_PERMS.read_messages = True
# membership
SAFE_PERMS.change_nickname = True
# text channel
SAFE_PERMS.send_messages = True
SAFE_PERMS.use_threads = True
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

    async def reply(self, ctx: GuildContext, content: str) -> Message:
        """Wraps `Context.reply()` with some extension-default boilerplate."""
        return await ctx.message.reply(
            content,
            allowed_mentions=AllowedMentions.none(),
        )

    def sort_role_pairs(self, role_pairs: List[RoleEntryPair]) -> List[RoleEntryPair]:
        # Sort by stringified role name.
        return sorted(role_pairs, key=lambda role_pair: str(role_pair[0]))

    def stringify_role_pairs(self, role_pairs: List[RoleEntryPair]) -> str:
        lines = []
        for role, role_entry in role_pairs:
            # Start with the role mention.
            role_line_parts = [f"{role.mention}"]
            # Mention that it's not joinable, if applicable.
            if not role_entry.joinable:
                role_line_parts.append(" (not joinable)")
            # Mention that it's not leavable, if applicable.
            if not role_entry.leavable:
                role_line_parts.append(" (not leavable)")
            # Add its description, if any.
            if role_entry.description:
                role_line_parts.append(f" {role_entry.description}")
            role_line = "".join(role_line_parts)
            lines.append(role_line)
        return "\n".join(lines)

    async def resolve_role(self, role_id: RoleID) -> Optional[Role]:
        # Attempt to resolve the role from the given ID.
        role = self.guild.get_role(role_id)
        # If the role resolves correctly, return it.
        if isinstance(role, Role):
            return role
        # Otherwise, warn about and automatically clean-up unresolved roles.
        self.log.warning(f"Cleaning-up unresolved role with ID: {role_id}")
        await self.store.deregister_role_by_id(self.guild.id, role_id)

    async def get_all_role_pairs(self) -> List[RoleEntryPair]:
        # Flatten the full list of role entry pairs.
        role_pairs: List[RoleEntryPair] = []
        role_entries = await self.store.get_all_role_entries(self.guild)
        for role_entry in role_entries:
            # If the role can be resolved, add it to the list.
            if role := await self.resolve_role(role_entry.role_id):
                role_pairs.append((role, role_entry))
        # Sort and return.
        return self.sort_role_pairs(role_pairs)

    async def get_relevant_role_for(
        self, role_entry: RoleEntry, member: Member
    ) -> Optional[Role]:
        # If the role can't be resolved, it certainly isn't relevant.
        if role := await self.resolve_role(role_entry.role_id):
            # A role is relevant to the user if:
            # 1. it's joinable; or
            # 2. it's leavable and present on the user.
            if role_entry.joinable or (role_entry.leavable and (role in member.roles)):
                return role

    async def get_relevant_role_pairs(self, member: Member) -> List[RoleEntryPair]:
        # Build a list of relevant role entry pairs.
        role_pairs: List[RoleEntryPair] = []
        role_entries = await self.store.get_all_role_entries(self.guild)
        for role_entry in role_entries:
            # If the role is relevant to the user, add it to the list.
            if role := await self.get_relevant_role_for(role_entry, member):
                role_pairs.append((role, role_entry))
        # Sort and return.
        return self.sort_role_pairs(role_pairs)

    async def get_unsafe_role_perms(self, role: Role) -> Optional[Permissions]:
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

    async def should_register_role(
        self, ctx: GuildContext, role: Role
    ) -> ConfirmationResult:
        # If the role contains unsafe permissions, ask for confirmation.
        if unsafe_perms := await self.get_unsafe_role_perms(role):
            unsafe_perms_str = "\n".join(
                f"- `{pname}`" for pname, pvalue in unsafe_perms if pvalue
            )
            conf_content = "\n".join(
                [
                    f"{role.mention} contains potentially unsafe permissions:",
                    unsafe_perms_str,
                    f"Do you want to register {role.mention} anyway?",
                ]
            )
            return await confirm_with_reaction(self.bot, ctx, conf_content)
        # Otherwise, the role can be registered right away.
        return ConfirmationResult.YES

    async def register_role(
        self,
        ctx: GuildContext,
        role: Role,
        joinable: bool,
        leavable: bool,
        description: Optional[str],
    ):
        # Check whether this is a role that should be registered. If the role
        # contains unsafe permissions, this will also ask for confirmation.
        conf = await self.should_register_role(ctx, role)
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
                await self.reply(
                    ctx,
                    f"✅ {role.mention} has been registered as opt-in/opt-out.",
                )
            elif role_entry.joinable:
                await self.reply(
                    ctx,
                    f"✅ {role.mention} has been registered as"
                    + " **opt-in only** (not leavable).",
                )
            elif role_entry.leavable:
                await self.reply(
                    ctx,
                    f"✅ {role.mention} has been registered as"
                    + " **opt-out only** (not joinable).",
                )
            else:
                await self.reply(
                    ctx,
                    f"✅ {role.mention} has been registered, but"
                    + " is **neither opt-in nor opt-out**.",
                )
        # If the answer was no, send a response.
        if conf == ConfirmationResult.NO:
            await self.reply(ctx, f"❌ {role.mention} has **not** been registered.")
        # If no answer was provided, don't do anything.

    async def deregister_role(self, ctx: GuildContext, role: Role):
        await self.store.deregister_role(role)
        await self.reply(ctx, f"✅ {role.mention} has been deregistered.")

    async def show_all_roles(self, ctx: GuildContext):
        if role_pairs := await self.get_all_role_pairs():
            role_pairs_str = self.stringify_role_pairs(role_pairs)
            await self.reply(
                ctx, f"There are {len(role_pairs)} roles registered:\n{role_pairs_str}"
            )
        else:
            await self.reply(ctx, f"🤷 There are no roles registered.")

    async def show_relevant_roles(self, ctx: MemberContext):
        # List only roles that are relevant to this user.
        member = ctx.author
        if role_pairs := await self.get_relevant_role_pairs(member):
            role_pairs_str = self.stringify_role_pairs(role_pairs)
            await self.reply(
                ctx,
                f"There are {len(role_pairs)} roles relevant to you:\n{role_pairs_str}",
            )
        else:
            await self.reply(ctx, f"🤷 There are no roles relevant to you.")

    async def join_roles(self, ctx: MemberContext, roles: List[Role]):
        await self.join_leave_roles(ctx, roles, JoinableRolesResult)

    async def leave_roles(self, ctx: MemberContext, roles: List[Role]):
        await self.join_leave_roles(ctx, roles, LeavableRolesResult)

    async def join_leave_roles(
        self, ctx: MemberContext, roles: List[Role], result_type: Type[RolesResult]
    ):
        if not roles:
            await self.reply(ctx, "🤔 You didn't provide any roles.")
            return
        member = ctx.author
        result = await result_type.build(self.store, member, roles)
        lines = await result.apply()
        content = "\n".join(lines)
        await self.reply(ctx, content)

    async def add_roles_to_members(
        self, ctx: MemberContext, roles: List[Role], members: List[Member]
    ):
        await self.add_remove_roles(ctx, roles, members, AddableRolesResult)

    async def remove_roles_from_members(
        self, ctx: MemberContext, roles: List[Role], members: List[Member]
    ):
        await self.add_remove_roles(ctx, roles, members, RemovableRolesResult)

    async def add_remove_roles(
        self,
        ctx: MemberContext,
        roles: List[Role],
        members: List[Member],
        result_type: Type[RolesResult],
    ):
        if not roles:
            await self.reply(ctx, "🤔 You didn't provide any roles.")
            return
        if not members:
            await self.reply(ctx, "🤔 You didn't provide any members.")
            return
        acting_user = ctx.author
        results = [
            await result_type.build(self.store, member, roles, acting_user)
            for member in members
        ]
        lines = []
        for result in results:
            result_lines = await result.apply()
            lines += result_lines
        content = "\n".join(lines)
        await self.reply(ctx, content)

    async def show_permitted_roles(self, ctx: GuildContext):
        permitted_roles = await self.store.get_permitted_roles(self.guild)
        if permitted_roles is not None:
            count_permitted_roles = len(permitted_roles)
            role_mentions = permitted_roles.to_mentions(self.guild)
            await self.reply(
                ctx,
                f"There are {count_permitted_roles} roles permitted to"
                + f" add/remove other users to/from roles: {role_mentions}",
            )
        else:
            await self.reply(
                ctx,
                f"No roles are permitted to add/remove other users to/from roles.",
            )

    async def set_permitted_roles(self, ctx: GuildContext, *roles: Role):
        if not roles:
            await self.reply(ctx, "🤷 No roles provided.")
            return
        new_permitted_roles = RoleSet(set(role.id for role in roles))
        new_role_mentions = new_permitted_roles.to_mentions(self.guild)
        old_permitted_roles = await self.store.set_permitted_roles(
            self.guild, new_permitted_roles
        )
        if old_permitted_roles is not None:
            old_role_mentions = old_permitted_roles.to_mentions(self.guild)
            await self.reply(
                ctx,
                f"✅ Changed permitted roles from {old_role_mentions}"
                + f" to: {new_role_mentions}",
            )
        else:
            await self.reply(ctx, f"✅ Changed permitted roles to: {new_role_mentions}")

    async def clear_permitted_roles(self, ctx: GuildContext):
        old_permitted_roles = await self.store.set_permitted_roles(self.guild, None)
        if old_permitted_roles is not None:
            role_mentions = old_permitted_roles.to_mentions(self.guild)
            await self.reply(ctx, f"✅ Cleared all permitted roles: {role_mentions}")
        else:
            await self.reply(
                ctx,
                f"🤷 No roles are permitted to add/remove other users to/from roles.",
            )

    async def member_has_permission(self, member: Member) -> bool:
        permitted_roles = await self.store.get_permitted_roles(self.guild)
        if permitted_roles is None:
            return False
        has_permission = permitted_roles.member_has_some(member)
        return has_permission
