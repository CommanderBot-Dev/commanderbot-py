from dataclasses import dataclass
from typing import List, Set

from discord import Member, Message, Role
from discord.ext.commands import Context

from commanderbot_ext._lib.cog_guild_state import CogGuildState
from commanderbot_ext.roles.roles_store import RolesStore


@dataclass
class RolesGuildState(CogGuildState):
    store: RolesStore

    async def can_join_role(self, ctx: Context, role: Role) -> bool:
        if role_entry := self.store.get_role_entry(role):
            # Only roles that are configured to be joinable are... joinable.
            return role_entry.joinable
        return False

    async def can_leave_role(self, ctx: Context, role: Role) -> bool:
        if self.store.get_role_entry(role):
            # Every configured role is implicitly leavable.
            return True
        return False

    async def list_roles(self, ctx: Context):
        # List roles in sorted order.
        if sorted_role_pairs := self.store.get_sorted_role_pairs(self.guild):
            lines = []
            count_roles = len(sorted_role_pairs)
            for role, role_entry in sorted_role_pairs:
                # Build the role title line.
                role_title_parts = [str(role)]
                if not role_entry.joinable:
                    role_title_parts.append(" (not joinable)")
                role_title_line = "".join(role_title_parts)
                lines.append(role_title_line)
            lines_str = "\n".join(lines)
            if count_roles > 1:
                heading = f"There are {count_roles} roles available:"
            else:
                heading = "There is *but a single* role available:"
            content = f"{heading}\n```\n{lines_str}\n```"
            await ctx.reply(content)
        else:
            await ctx.reply(f"There are no roles available.")

    async def join_roles(self, ctx: Context, roles: List[Role]):
        member = ctx.author
        assert isinstance(member, Member)
        # Summarize what happens with each role so we can print a full response later.
        passed_roles: Set[Role] = set()
        failed_roles: Set[Role] = set()
        # Process one role at a time...
        for role in roles:
            # Check whether the user can join this role.
            if self.can_join_role(ctx, role):
                passed_roles.add(role)
            else:
                failed_roles.add(role)
        # Build a response out of several lines.
        response_lines = []
        # Add them to and let them know about any roles they have joined.
        if passed_roles:
            await member.add_roles(passed_roles, reason="User opted-in to roles")
            passed_roles_str = "`, `".join(str(r) for r in passed_roles)
            response_lines.append(f"You have joined `{passed_roles_str}`")
        # Let them know about any roles they tried to join but could not.
        if failed_roles:
            failed_roles_str = "`, `".join(str(r) for r in failed_roles)
            response_lines.append(f"You cannot join `{failed_roles_str}`")
        # Let them know if their roles have not changed.
        else:
            response_lines.append(f"Your roles have not changed.")
        # Send the final response.
        response_content = "\n".join(response_lines)
        await ctx.reply(response_content)

    async def leave_roles(self, ctx: Context, roles: List[Role]):
        member = ctx.author
        assert isinstance(member, Member)
        # Summarize what happens with each role so we can print a full response later.
        passed_roles: Set[Role] = set()
        failed_roles: Set[Role] = set()
        # Process one role at a time...
        for role in roles:
            # Check whether the user can leave this role.
            if self.can_leave_role(ctx, role):
                passed_roles.add(role)
            else:
                failed_roles.add(role)
        # Build a response out of several lines.
        response_lines = []
        # Remove them from and let them know about any roles they have left.
        if passed_roles:
            await member.remove_roles(passed_roles, reason="User opted-out of roles")
            passed_roles_str = "`, `".join(str(r) for r in passed_roles)
            response_lines.append(f"You have left `{passed_roles_str}`")
        # Let them know about any roles they tried to leave but could not.
        if failed_roles:
            failed_roles_str = "`, `".join(str(r) for r in failed_roles)
            response_lines.append(f"You cannot leave `{failed_roles_str}`")
        # Let them know if their roles have not changed.
        else:
            response_lines.append(f"Your roles have not changed.")
        # Send the final response.
        response_content = "\n".join(response_lines)
        await ctx.reply(response_content)

    async def add_role(self, ctx: Context, role: Role, joinable: bool):
        if self.store.add_role(role, joinable):
            await ctx.reply(f"Added `{role}` to opt-in roles.")

    async def remove_role(self, ctx: Context, role: Role):
        if self.store.remove_role(role):
            await ctx.reply(f"Removed `{role}` from opt-in roles.")
