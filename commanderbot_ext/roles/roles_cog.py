from commanderbot_lib import checks
from discord import Member, Role
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
            await self.state.show_relevant_roles(ctx)

    @cmd_roles.command(name="register")
    @checks.is_administrator()
    async def cmd_roles_register(
        self, ctx: Context, role: Role, joinable: bool = True, leavable: bool = True
    ):
        await self.state.register_role(ctx, role, joinable=joinable, leavable=leavable)

    @cmd_roles.command(name="deregister")
    @checks.is_administrator()
    async def cmd_roles_deregister(self, ctx: Context, role: Role):
        await self.state.deregister_role(ctx, role)

    @cmd_roles.command(name="all")
    @checks.is_administrator()
    async def cmd_roles_all(self, ctx: Context):
        await self.state.show_all_roles(ctx)

    @cmd_roles.command(name="show")
    async def cmd_roles_show(self, ctx: Context):
        await self.state.show_relevant_roles(ctx)

    @cmd_roles.command(name="join")
    async def cmd_roles_join(self, ctx: Context, role: Role):
        await self.state.join_role(ctx, role)

    @cmd_roles.command(name="leave")
    async def cmd_roles_leave(self, ctx: Context, role: Role):
        await self.state.leave_role(ctx, role)

    @command(name="join")
    async def cmd_join(self, ctx: Context, role: Role):
        await self.state.join_role(ctx, role)

    @command(name="leave")
    async def cmd_leave(self, ctx: Context, role: Role):
        await self.state.leave_role(ctx, role)
