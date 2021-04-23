from typing import Optional

from discord import Member
from discord.ext.commands import Bot, Cog, command, group

from commanderbot_ext.ext.roles.roles_data import RolesData
from commanderbot_ext.ext.roles.roles_guild_state import RolesGuildState
from commanderbot_ext.ext.roles.roles_json_store import RolesJsonStore
from commanderbot_ext.ext.roles.roles_options import RolesOptions
from commanderbot_ext.ext.roles.roles_state import RolesState
from commanderbot_ext.ext.roles.roles_store import RolesStore
from commanderbot_ext.lib import (
    CogGuildStateManager,
    GuildContext,
    GuildRole,
    InMemoryDatabaseOptions,
    JsonFileDatabaseAdapter,
    JsonFileDatabaseOptions,
    UnsupportedDatabaseOptions,
    checks,
)


def make_roles_store(bot: Bot, cog: Cog, options: RolesOptions) -> RolesStore:
    db_options = options.database
    if isinstance(db_options, InMemoryDatabaseOptions):
        return RolesData()
    if isinstance(db_options, JsonFileDatabaseOptions):
        return RolesJsonStore(
            bot=bot,
            cog=cog,
            db=JsonFileDatabaseAdapter(
                options=db_options,
                serializer=lambda cache: cache.serialize(),
                deserializer=RolesData.deserialize,
            ),
        )
    raise UnsupportedDatabaseOptions(db_options)


class RolesCog(Cog, name="commanderbot_ext.ext.roles"):
    """
    Allows users to opt-in/out to/from configurable roles.

    Attributes
    ----------
    bot
        The bot/client instance this cog is attached to.
    options
        Immutable, pre-defined settings that define core cog behaviour.
    store
        Abstracts the data storage and persistence of this cog.
    state
        Encapsulates the state and logic of this cog, for each guild.
    """

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
                factory=lambda guild: RolesGuildState(
                    bot=bot, cog=self, guild=guild, store=self.store
                ),
            ),
            store=self.store,
        )

    # @@ COMMANDS

    # @@ join

    @command(
        name="join",
        brief="Join a role.",
    )
    @checks.guild_only()
    async def cmd_join(self, ctx: GuildContext, role: GuildRole):
        await self.state[ctx.guild].join_role(ctx, role)

    # @@ leave

    @command(
        name="leave",
        brief="Leave a role.",
    )
    @checks.guild_only()
    async def cmd_leave(self, ctx: GuildContext, role: GuildRole):
        await self.state[ctx.guild].leave_role(ctx, role)

    # @@ roles

    @group(
        name="roles",
        brief="Show relevant roles.",
    )
    @checks.guild_only()
    async def cmd_roles(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await self.state[ctx.guild].show_relevant_roles(ctx)

    # @@ roles show

    @cmd_roles.command(
        name="show",
        brief="Show relevant roles.",
    )
    async def cmd_roles_show(self, ctx: GuildContext):
        await self.state[ctx.guild].show_relevant_roles(ctx)

    # @@ roles join

    @cmd_roles.command(
        name="join",
        brief="Join a role.",
    )
    async def cmd_roles_join(self, ctx: GuildContext, role: GuildRole):
        await self.state[ctx.guild].join_role(ctx, role)

    # @@ roles leave

    @cmd_roles.command(
        name="leave",
        brief="Leave a role.",
    )
    async def cmd_roles_leave(self, ctx: GuildContext, role: GuildRole):
        await self.state[ctx.guild].leave_role(ctx, role)

    # @@ roles showall

    @cmd_roles.command(
        name="showall",
        brief="Show all roles.",
    )
    @checks.is_administrator()
    async def cmd_roles_showall(self, ctx: GuildContext):
        await self.state[ctx.guild].show_all_roles(ctx)

    # @@ roles add

    @cmd_roles.command(
        name="add",
        brief="Add a role to members.",
    )
    @checks.is_administrator()
    async def cmd_roles_add(self, ctx: GuildContext, role: GuildRole, *members: Member):
        await self.state[ctx.guild].add_role_to_members(ctx, role, list(members))

    # @@ roles remove

    @cmd_roles.command(
        name="remove",
        brief="Remove a role from members.",
    )
    @checks.is_administrator()
    async def cmd_roles_remove(
        self, ctx: GuildContext, role: GuildRole, *members: Member
    ):
        await self.state[ctx.guild].remove_role_from_members(ctx, role, list(members))

    # @@ roles register

    @cmd_roles.command(
        name="register",
        brief="Register a role.",
    )
    @checks.is_administrator()
    async def cmd_roles_register(
        self,
        ctx: GuildContext,
        role: GuildRole,
        joinable: bool = True,
        leavable: bool = True,
        *,
        description: Optional[str],
    ):
        await self.state[ctx.guild].register_role(
            ctx,
            role,
            joinable=joinable,
            leavable=leavable,
            description=description,
        )

    # @@ roles deregister

    @cmd_roles.command(
        name="deregister",
        brief="Deregister a role.",
    )
    @checks.is_administrator()
    async def cmd_roles_deregister(self, ctx: GuildContext, role: GuildRole):
        await self.state[ctx.guild].deregister_role(ctx, role)
