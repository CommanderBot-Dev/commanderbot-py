from dataclasses import dataclass

from commanderbot_lib import checks
from discord import Guild, Member
from discord.ext.commands import Bot, Cog, command, group

from commanderbot_ext._lib.cog_guild_state_factory import CogGuildStateFactory
from commanderbot_ext._lib.cog_guild_state_manager import CogGuildStateManager
from commanderbot_ext._lib.database_adapter import JsonFileDatabaseAdapter
from commanderbot_ext._lib.database_options import (
    InMemoryDatabaseOptions,
    JsonFileDatabaseOptions,
    UnsupportedDatabaseOptions,
)
from commanderbot_ext._lib.types import GuildContext, GuildRole
from commanderbot_ext.roles.roles_guild_state import RolesGuildState
from commanderbot_ext.roles.roles_json_store import RolesJsonStore
from commanderbot_ext.roles.roles_options import RolesOptions
from commanderbot_ext.roles.roles_state import RolesState
from commanderbot_ext.roles.roles_store import RolesStore


def make_roles_store(bot: Bot, cog: Cog, options: RolesOptions) -> RolesStore:
    db_options = options.database
    if isinstance(db_options, InMemoryDatabaseOptions):
        return RolesJsonStore(bot=bot, cog=cog)
    if isinstance(db_options, JsonFileDatabaseOptions):
        return RolesJsonStore(
            bot=bot, cog=cog, db=JsonFileDatabaseAdapter(options=db_options)
        )
    raise UnsupportedDatabaseOptions(db_options)


def make_guild_state_factory(
    bot: Bot, cog: Cog, store: RolesStore
) -> CogGuildStateFactory:
    def _make_guild_state(guild: Guild) -> RolesGuildState:
        return RolesGuildState(bot=bot, cog=cog, guild=guild, store=store)

    return _make_guild_state


class RolesCog(Cog, name="commanderbot_ext.roles"):
    def __init__(self, bot: Bot, **options):
        self.bot = bot
        self.options = RolesOptions.from_dict(options)
        self.store: RolesStore = make_roles_store(bot, self, self.options)
        self.state = RolesState(
            bot=self.bot,
            cog=self,
            guilds=CogGuildStateManager(
                bot=self.bot,
                cog=self,
                factory=make_guild_state_factory(bot, self, self.store),
            ),
            store=self.store,
        )

    @group(name="roles")
    @checks.guild_only()
    async def cmd_roles(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await self.state[ctx.guild].show_relevant_roles(ctx)

    @cmd_roles.command(name="register")
    @checks.is_administrator()
    async def cmd_roles_register(
        self,
        ctx: GuildContext,
        role: GuildRole,
        joinable: bool = True,
        leavable: bool = True,
    ):
        await self.state[ctx.guild].register_role(
            ctx, role, joinable=joinable, leavable=leavable
        )

    @cmd_roles.command(name="deregister")
    @checks.is_administrator()
    async def cmd_roles_deregister(self, ctx: GuildContext, role: GuildRole):
        await self.state[ctx.guild].deregister_role(ctx, role)

    @cmd_roles.command(name="add")
    @checks.is_administrator()
    async def cmd_roles_add(self, ctx: GuildContext, role: GuildRole, *members: Member):
        await self.state[ctx.guild].add_role_to_members(ctx, role, list(members))

    @cmd_roles.command(name="remove")
    @checks.is_administrator()
    async def cmd_roles_remove(
        self, ctx: GuildContext, role: GuildRole, *members: Member
    ):
        await self.state[ctx.guild].remove_role_from_members(ctx, role, list(members))

    @cmd_roles.command(name="all")
    @checks.is_administrator()
    async def cmd_roles_all(self, ctx: GuildContext):
        await self.state[ctx.guild].show_all_roles(ctx)

    @cmd_roles.command(name="show")
    async def cmd_roles_show(self, ctx: GuildContext):
        await self.state[ctx.guild].show_relevant_roles(ctx)

    @cmd_roles.command(name="join")
    async def cmd_roles_join(self, ctx: GuildContext, role: GuildRole):
        await self.state[ctx.guild].join_role(ctx, role)

    @cmd_roles.command(name="leave")
    async def cmd_roles_leave(self, ctx: GuildContext, role: GuildRole):
        await self.state[ctx.guild].leave_role(ctx, role)

    @command(name="join")
    @checks.guild_only()
    async def cmd_join(self, ctx: GuildContext, role: GuildRole):
        await self.state[ctx.guild].join_role(ctx, role)

    @command(name="leave")
    @checks.guild_only()
    async def cmd_leave(self, ctx: GuildContext, role: GuildRole):
        await self.state[ctx.guild].leave_role(ctx, role)
