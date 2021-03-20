from typing import List

from commanderbot_lib import checks
from discord import Message, Role
from discord.ext.commands import Bot, Cog, Context, command, group

from commanderbot_ext._lib.cog_guild_state_manager import CogGuildStateManager
from commanderbot_ext.roles.roles_guild_state_factory import RolesGuildStateFactory
from commanderbot_ext.roles.roles_options import RolesOptions
from commanderbot_ext.roles.roles_state import RolesState
from commanderbot_ext.roles.roles_store import RolesStore


class RolesCog(Cog, name="commanderbot_ext.roles"):
    def __init__(self, bot: Bot, **options):
        self.bot = bot
        self.options = RolesOptions(**options)
        self.store = RolesStore(bot=self.bot, cog=self, database=self.options.database)
        self.state = RolesState(
            bot=self.bot,
            cog=self,
            guild_states=CogGuildStateManager(
                bot=self.bot,
                cog=self,
                factory=RolesGuildStateFactory(
                    bot=self.bot, cog=self, store=self.store
                ),
            ),
            store=self.store,
        )

    @group(name="roles")
    async def cmd_roles(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await self.state.list_roles(ctx)

    @cmd_roles.command(name="list")
    async def cmd_roles_list(self, ctx: Context):
        await self.state.list_roles(ctx)

    @cmd_roles.command(name="join")
    async def cmd_roles_join(self, ctx: Context, *, roles: List[Role]):
        await self.state.join_roles(ctx, roles)

    @cmd_roles.command(name="leave")
    async def cmd_roles_leave(self, ctx: Context, *, roles: List[Role]):
        await self.state.leave_roles(ctx, roles)

    @cmd_roles.command(name="add")
    @checks.is_administrator()
    async def cmd_roles_add(self, ctx: Context, role: Role, joinable: bool = True):
        await self.state.add_role(ctx, role, joinable)

    @cmd_roles.command(name="remove")
    @checks.is_administrator()
    async def cmd_roles_remove(self, ctx: Context, role: Role):
        await self.state.remove_role(ctx, role)

    @command(name="join")
    async def cmd_join(self, ctx: Context, *, roles: List[Role]):
        await self.state.join_roles(ctx, roles)

    @command(name="leave")
    async def cmd_leave(self, ctx: Context, *, roles: List[Role]):
        await self.state.leave_roles(ctx, roles)
