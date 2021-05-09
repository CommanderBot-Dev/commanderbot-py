from typing import Optional

from discord.ext.commands import Bot, Cog, command, group

from commanderbot_ext.ext.invite.invite_data import InviteData
from commanderbot_ext.ext.invite.invite_guild_state import InviteGuildState
from commanderbot_ext.ext.invite.invite_json_store import InviteJsonStore
from commanderbot_ext.ext.invite.invite_options import InviteOptions
from commanderbot_ext.ext.invite.invite_state import InviteState
from commanderbot_ext.ext.invite.invite_store import InviteStore
from commanderbot_ext.lib import (
    CogGuildStateManager,
    GuildContext,
    InMemoryDatabaseOptions,
    JsonFileDatabaseAdapter,
    JsonFileDatabaseOptions,
    UnsupportedDatabaseOptions,
    checks,
)


def make_invite_store(bot: Bot, cog: Cog, options: InviteOptions) -> InviteStore:
    db_options = options.database
    if isinstance(db_options, InMemoryDatabaseOptions):
        return InviteData()
    if isinstance(db_options, JsonFileDatabaseOptions):
        return InviteJsonStore(
            bot=bot,
            cog=cog,
            db=JsonFileDatabaseAdapter(
                options=db_options,
                serializer=lambda cache: cache.serialize(),
                deserializer=InviteData.deserialize,
            ),
        )
    raise UnsupportedDatabaseOptions(db_options)


class InviteCog(Cog, name="commanderbot_ext.ext.invite"):
    """
    Allows invites for other servers to be added and listed.

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
        self.bot: Bot = bot
        self.bot = bot
        self.options = InviteOptions.from_dict(options)
        self.store: InviteStore = make_invite_store(bot, self, self.options)
        self.state = InviteState(
            bot=self.bot,
            cog=self,
            guilds=CogGuildStateManager(
                bot=self.bot,
                cog=self,
                factory=lambda guild: InviteGuildState(
                    bot=bot, cog=self, guild=guild, store=self.store
                ),
            ),
            store=self.store,
        )

    # @@ COMMANDS

    # @@ invite

    @command(
        name="invite",
        brief="Show invites.",
    )
    @checks.guild_only()
    async def cmd_invite(self, ctx: GuildContext, *, invite_query: Optional[str]):
        if invite_query:
            await self.state[ctx.guild].show_invite(ctx, invite_query)
        else:
            await self.state[ctx.guild].show_guild_invite(ctx)

    # @@ invites

    @group(
        name="invites",
        brief="Manage invites, or list all invites.",
    )
    @checks.guild_only()
    async def cmd_invites(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            if ctx.subcommand_passed:
                await ctx.send_help(self.cmd_invites)
            else:
                await self.state[ctx.guild].list_invites(ctx)

    @cmd_invites.command(
        name="details",
        brief="Show the details of invites.",
    )
    async def cmd_invites_details(self, ctx: GuildContext, *, invite_query: str):
        await self.state[ctx.guild].show_invite_details(ctx, invite_query)

    # @@ invites add

    @cmd_invites.command(
        name="add",
        brief="Add an invite.",
    )
    @checks.is_administrator()
    async def cmd_invites_add(self, ctx: GuildContext, invite_key: str, link: str):
        await self.state[ctx.guild].add_invite(ctx, invite_key, link=link)

    # @@ invites remove

    @cmd_invites.command(
        name="remove",
        brief="Remove an invite.",
    )
    @checks.is_administrator()
    async def cmd_invites_remove(self, ctx: GuildContext, invite_key: str):
        await self.state[ctx.guild].remove_invite(ctx, invite_key)

    # @@ invites modify

    @cmd_invites.group(
        name="modify",
        brief="Modify an invite.",
    )
    @checks.is_administrator()
    async def cmd_invites_modify(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_invites_modify)

    @cmd_invites_modify.command(
        name="link",
        brief="Modify an invite's link.",
    )
    async def cmd_invites_modify_link(
        self, ctx: GuildContext, invite_key: str, link: str
    ):
        await self.state[ctx.guild].modify_invite_link(ctx, invite_key, link)

    @cmd_invites_modify.command(
        name="tags",
        brief="Modify an invite's tags.",
    )
    async def cmd_invites_modify_tags(
        self, ctx: GuildContext, invite_key: str, *tags: str
    ):
        await self.state[ctx.guild].modify_invite_tags(ctx, invite_key, tags)

    @cmd_invites_modify.command(
        name="description", brief="Modify an invite's description"
    )
    async def cmd_invites_modify_description(
        self, ctx: GuildContext, invite_key: str, *, description: Optional[str]
    ):
        await self.state[ctx.guild].modify_invite_description(
            ctx, invite_key, description
        )

    # @@ invites configure

    @cmd_invites.group(
        name="configure",
        aliases=["cfg"],
        brief="Configure invite settings.",
    )
    @checks.is_administrator()
    async def cmd_invites_configure(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_invites_configure)

    @cmd_invites_configure.command(
        name="here",
        brief="Configure the invite key for this guild.",
    )
    async def cmd_invites_configure_here(
        self, ctx: GuildContext, *, invite_key: Optional[str] = None
    ):
        await self.state[ctx.guild].configure_guild_key(ctx, invite_key)
