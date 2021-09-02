from typing import Optional, cast

from discord import Color, Message, TextChannel, Thread, User
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context

from commanderbot.core.commander_bot_base import CommanderBotBase
from commanderbot.ext.stacktracer.stacktracer_data import StacktracerData
from commanderbot.ext.stacktracer.stacktracer_guild_state import StacktracerGuildState
from commanderbot.ext.stacktracer.stacktracer_json_store import StacktracerJsonStore
from commanderbot.ext.stacktracer.stacktracer_options import StacktracerOptions
from commanderbot.ext.stacktracer.stacktracer_state import StacktracerState
from commanderbot.ext.stacktracer.stacktracer_store import StacktracerStore
from commanderbot.lib import (
    CogGuildStateManager,
    EventData,
    GuildContext,
    InMemoryDatabaseOptions,
    JsonFileDatabaseAdapter,
    JsonFileDatabaseOptions,
    UnsupportedDatabaseOptions,
    checks,
)


def _make_store(bot: Bot, cog: Cog, options: StacktracerOptions) -> StacktracerStore:
    db_options = options.database
    if isinstance(db_options, InMemoryDatabaseOptions):
        return StacktracerData()
    if isinstance(db_options, JsonFileDatabaseOptions):
        return StacktracerJsonStore(
            bot=bot,
            cog=cog,
            db=JsonFileDatabaseAdapter(
                options=db_options,
                serializer=lambda cache: cache.to_json(),
                deserializer=StacktracerData.from_data,
            ),
        )
    raise UnsupportedDatabaseOptions(db_options)


class StacktracerCog(Cog, name="commanderbot.ext.stacktracer"):
    """
    Prints errors and stacktraces to a channel for staff to see.

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
        self.options = StacktracerOptions.from_data(options)
        self.store: StacktracerStore = _make_store(bot, self, self.options)
        self.state = StacktracerState(
            bot=self.bot,
            cog=self,
            guilds=CogGuildStateManager(
                bot=self.bot,
                cog=self,
                factory=lambda guild: StacktracerGuildState(
                    bot=bot, cog=self, guild=guild, store=self.store
                ),
            ),
            store=self.store,
        )

        # Register error handlers with the bot core.
        if isinstance(bot, CommanderBotBase):
            bot.add_event_error_handler(self.handle_event_error)
            bot.add_command_error_handler(self.handle_command_error)

    async def handle_event_error(
        self, error: Exception, event_data: EventData, handled: bool
    ) -> Optional[bool]:
        return await self.state.handle_event_error(error, event_data, handled)

    async def handle_command_error(
        self, error: Exception, ctx: Context, handled: bool
    ) -> Optional[bool]:
        return await self.state.handle_command_error(error, ctx, handled)

    @Cog.listener()
    async def on_message_delete(self, message: Message):
        expected = f"{self.bot.command_prefix}stacktracer test"
        author = cast(User, message.author)
        if (message.content == expected) and await self.bot.is_owner(author):
            raise Exception("Testing the error logging configuration for events.")

    # @@ COMMANDS

    # @@ stacktracer

    @commands.group(
        name="stacktracer",
        brief="Manage error logging globally and across guilds.",
    )
    @checks.is_guild_admin_or_bot_owner()
    async def cmd_stacktracer(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_stacktracer)

    @cmd_stacktracer.command(
        name="test",
        brief="Test the error logging configuration for commands.",
    )
    async def cmd_stacktracer_test(self, ctx: GuildContext):
        raise Exception("Testing the error logging configuration for commands.")

    # @@ stacktracer global

    @cmd_stacktracer.group(
        name="global",
        brief="Manage global error logging.",
    )
    @checks.is_owner()
    async def cmd_stacktracer_global(self, ctx: Context):
        if not ctx.invoked_subcommand:
            if ctx.subcommand_passed:
                await ctx.send_help(self.cmd_stacktracer_global)
            else:
                await self.state.show_global_log_options(ctx)

    @cmd_stacktracer_global.command(
        name="show",
        brief="Show the global error logging configuration.",
    )
    async def cmd_stacktracer_global_show(self, ctx: Context):
        await self.state.show_global_log_options(ctx)

    @cmd_stacktracer_global.command(
        name="set",
        brief="Set the global error logging configuration.",
    )
    async def cmd_stacktracer_global_set(
        self,
        ctx: Context,
        channel: TextChannel | Thread,
        stacktrace: Optional[bool],
        emoji: Optional[str],
        color: Optional[Color],
    ):
        await self.state.set_global_log_options(
            ctx,
            channel=channel,
            stacktrace=stacktrace,
            emoji=emoji,
            color=color,
        )

    @cmd_stacktracer_global.command(
        name="remove",
        brief="Remove the global error logging configuration.",
    )
    async def cmd_stacktracer_global_remove(self, ctx: Context):
        await self.state.remove_global_log_options(ctx)

    # @@ stacktracer guild

    @cmd_stacktracer.group(
        name="guild",
        brief="Manage error logging for this guild.",
    )
    @checks.guild_only()
    async def cmd_stacktracer_guild(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            if ctx.subcommand_passed:
                await ctx.send_help(self.cmd_stacktracer_guild)
            else:
                await self.state[ctx.guild].show_guild_log_options(ctx)

    @cmd_stacktracer_guild.command(
        name="show",
        brief="Show the error logging configuration for this guild.",
    )
    async def cmd_stacktracer_guild_show(self, ctx: GuildContext):
        await self.state[ctx.guild].show_guild_log_options(ctx)

    @cmd_stacktracer_guild.command(
        name="set",
        brief="Set the error logging configuration for this guild.",
    )
    async def cmd_stacktracer_guild_set(
        self,
        ctx: GuildContext,
        channel: TextChannel | Thread,
        stacktrace: Optional[bool],
        emoji: Optional[str],
        color: Optional[Color],
    ):
        await self.state[ctx.guild].set_guild_log_options(
            ctx,
            channel=channel,
            stacktrace=stacktrace,
            emoji=emoji,
            color=color,
        )

    @cmd_stacktracer_guild.command(
        name="remove",
        brief="Remove the error logging configuration for this guild.",
    )
    async def cmd_stacktracer_guild_remove(self, ctx: GuildContext):
        await self.state[ctx.guild].remove_guild_log_options(ctx)
