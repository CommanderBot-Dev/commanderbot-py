from datetime import datetime
from typing import Optional, Union

from discord import CategoryChannel, TextChannel
from discord.ext.commands import Bot, Cog, group

from commanderbot_ext.ext.help_chat import constants
from commanderbot_ext.ext.help_chat.help_chat_guild_state import HelpChatGuildState
from commanderbot_ext.ext.help_chat.help_chat_options import HelpChatOptions
from commanderbot_ext.ext.help_chat.help_chat_state import HelpChatState
from commanderbot_ext.ext.help_chat.help_chat_store import HelpChatStore
from commanderbot_ext.ext.help_chat.sql_store import HelpChatSQLStore
from commanderbot_ext.lib import (
    CogGuildStateManager,
    GuildContext,
    InMemoryDatabaseOptions,
    SQLiteDatabaseAdapter,
    SQLiteDatabaseOptions,
    UnsupportedDatabaseOptions,
    checks,
)


def make_help_chat_store(bot: Bot, cog: Cog, options: HelpChatOptions) -> HelpChatStore:
    db_options = options.database
    if isinstance(db_options, InMemoryDatabaseOptions):
        return HelpChatSQLStore(
            bot=bot,
            cog=cog,
            db=SQLiteDatabaseAdapter(options=SQLiteDatabaseOptions.in_memory()),
        )
    if isinstance(db_options, SQLiteDatabaseOptions):
        return HelpChatSQLStore(
            bot=bot,
            cog=cog,
            db=SQLiteDatabaseAdapter(options=db_options),
        )
    raise UnsupportedDatabaseOptions(db_options)


class HelpChatCog(Cog, name="commanderbot_ext.ext.help_chat"):
    """
    Designate channels to be recycled for question-and-answer threads.

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
        self.options = HelpChatOptions.from_dict(options)
        self.store: HelpChatStore = make_help_chat_store(bot, self, self.options)
        self.state = HelpChatState(
            bot=self.bot,
            cog=self,
            guilds=CogGuildStateManager(
                bot=self.bot,
                cog=self,
                factory=lambda guild: HelpChatGuildState(
                    bot=bot, cog=self, guild=guild, store=self.store
                ),
            ),
            store=self.store,
        )

    # @@ COMMANDS

    @group(name="helpchat", aliases=["hc"])
    @checks.is_administrator()
    @checks.guild_only()
    async def cmd_helpchat(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_helpchat)

    # @@ helpchat channels

    @cmd_helpchat.group(name="channels", aliases=["ch"])
    async def cmd_helpchat_channels(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_helpchat_channels)

    @cmd_helpchat_channels.command(name="list")
    async def cmd_helpchat_channels_list(self, ctx: GuildContext):
        await self.state[ctx.guild].list_channels(ctx)

    @cmd_helpchat_channels.command(name="add")
    async def cmd_helpchat_channels_add(
        self, ctx: GuildContext, *channels: Union[TextChannel, CategoryChannel]
    ):
        if not channels:
            await ctx.send_help(self.cmd_helpchat_channels_add)
        await self.state[ctx.guild].add_channels(ctx, channels)

    @cmd_helpchat_channels.command(name="remove")
    async def cmd_helpchat_channels_remove(
        self, ctx: GuildContext, *channels: Union[TextChannel, CategoryChannel]
    ):
        if not channels:
            await ctx.send_help(self.cmd_helpchat_channels_remove)
        await self.state[ctx.guild].remove_channels(ctx, channels)

    # @@ helpchat report

    @cmd_helpchat.group(name="report")
    async def cmd_helpchat_report(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_helpchat_report)

    # @@ helpchat report build

    @cmd_helpchat_report.command(name="build")
    async def cmd_helpchat_report_build(
        self,
        ctx: GuildContext,
        after: str,
        before: str = "now",
        label: Optional[str] = None,
        split_length: int = constants.DEFAULT_REPORT_SPLIT_LENGTH,
        max_rows: int = constants.DEFAULT_REPORT_MAX_ROWS,
        min_score: int = constants.DEFAULT_REPORT_MIN_SCORE,
    ):
        after_date = datetime.strptime(after, constants.DATE_FMT_YYYY_MM_DD)
        before_date = (
            datetime.utcnow()
            if before == "now"
            else datetime.strptime(before, constants.DATE_FMT_YYYY_MM_DD)
        )
        actual_label = (
            label
            if label is not None
            else datetime.utcnow().strftime(constants.DATE_FMT_YYYY_MM_DD_HH_MM_SS)
        )
        await self.state[ctx.guild].build_report(
            ctx,
            after_date,
            before_date,
            label=actual_label,
            split_length=split_length,
            max_rows=max_rows,
            min_score=min_score,
        )
