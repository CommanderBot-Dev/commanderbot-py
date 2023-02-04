from typing import Optional, Union, cast

from discord import Guild, Interaction, Message, TextChannel, Thread, User
from discord.app_commands import (
    Group,
    Transform,
    command,
    default_permissions,
    guild_only,
)
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context, GroupCog

from commanderbot.core.commander_bot_base import CommanderBotBase
from commanderbot.ext.stacktracer.stacktracer_data import StacktracerData
from commanderbot.ext.stacktracer.stacktracer_exceptions import (
    TestAppCommandErrors,
    TestCommandErrors,
    TestEventErrors,
)
from commanderbot.ext.stacktracer.stacktracer_guild_state import StacktracerGuildState
from commanderbot.ext.stacktracer.stacktracer_json_store import StacktracerJsonStore
from commanderbot.ext.stacktracer.stacktracer_options import StacktracerOptions
from commanderbot.ext.stacktracer.stacktracer_state import StacktracerState
from commanderbot.ext.stacktracer.stacktracer_store import StacktracerStore
from commanderbot.lib import (
    CogGuildStateManager,
    Color,
    EventData,
    InMemoryDatabaseOptions,
    JsonFileDatabaseAdapter,
    JsonFileDatabaseOptions,
    UnsupportedDatabaseOptions,
)
from commanderbot.lib.commands import checks as command_checks
from commanderbot.lib.interactions import ColorTransformer, EmojiTransformer, checks


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


@guild_only()
@default_permissions(administrator=True)
class StacktracerCog(
    GroupCog,
    name="commanderbot.ext.stacktracer",
    group_name="stacktracer",
    description="Manage error logging globally and across guilds",
):
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
            bot.add_app_command_error_handler(self.handle_app_command_error)

    async def handle_event_error(
        self, error: Exception, event_data: EventData, handled: bool
    ) -> Optional[bool]:
        return await self.state.handle_event_error(error, event_data, handled)

    async def handle_command_error(
        self, error: Exception, ctx: Context, handled: bool
    ) -> Optional[bool]:
        return await self.state.handle_command_error(error, ctx, handled)

    async def handle_app_command_error(
        self, error: Exception, interaction: Interaction, handled: bool
    ) -> Optional[bool]:
        return await self.state.handle_app_command_error(error, interaction, handled)

    @Cog.listener()
    async def on_message_delete(self, message: Message):
        expected = f"{self.bot.command_prefix}stacktracer test"
        author = cast(User, message.author)
        if (message.content == expected) and await self.bot.is_owner(author):
            raise TestEventErrors

    # @@ COMMANDS

    # @@ stacktracer test

    # Commands
    @commands.group(
        name="stacktracer",
        brief="Manage error logging",
    )
    @commands.guild_only()
    @command_checks.is_guild_admin_or_bot_owner()
    async def cmd_stacktracer(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_stacktracer)

    @cmd_stacktracer.command(
        name="test",
        brief="Test the error logging configuration for commands",
    )
    async def cmd_stacktracer_test(self, ctx: Context):
        raise TestCommandErrors

    # App commands
    @command(
        name="test", description="Test the error logging configuration for app commands"
    )
    async def cmd_stacktracer_test_app(self, interaction: Interaction):
        await interaction.response.send_message("Raising an exception...")
        raise TestAppCommandErrors

    # @@ stacktracer global

    # Groups
    cmd_global = Group(name="global", description="Manage global error logging")

    # App commands
    @cmd_global.command(
        name="show", description="Show the global error logging configuration"
    )
    @checks.is_owner()
    async def cmd_stacktracer_global_show(self, interaction: Interaction):
        await self.state.show_global_log_options(interaction)

    @cmd_global.command(
        name="set",
        description="Set the global error logging configuration",
    )
    @checks.is_owner()
    async def cmd_stacktracer_global_set(
        self,
        interaction: Interaction,
        channel: Union[TextChannel, Thread],
        stacktrace: Optional[bool],
        emoji: Optional[Transform[str, EmojiTransformer]],
        color: Optional[Transform[Color, ColorTransformer]],
    ):
        await self.state.set_global_log_options(
            interaction,
            channel=channel,
            stacktrace=stacktrace,
            emoji=emoji,
            color=color,
        )

    @cmd_global.command(
        name="remove",
        description="Remove the global error logging configuration",
    )
    @checks.is_owner()
    async def cmd_stacktracer_global_remove(
        self,
        interaction: Interaction,
    ):
        await self.state.remove_global_log_options(interaction)

    # @@ stacktracer guild

    # Groups
    cmd_guild = Group(name="guild", description="Manage error logging for this guild")

    # App commands
    @cmd_guild.command(
        name="show",
        description="Show the error logging configuration for this guild",
    )
    async def cmd_stacktracer_guild_show(self, interaction: Interaction):
        assert isinstance(interaction.guild, Guild)
        await self.state[interaction.guild].show_guild_log_options(interaction)

    @cmd_guild.command(
        name="set",
        description="Set the error logging configuration for this guild",
    )
    async def cmd_stacktracer_guild_set(
        self,
        interaction: Interaction,
        channel: Union[TextChannel, Thread],
        stacktrace: Optional[bool],
        emoji: Optional[Transform[str, EmojiTransformer]],
        color: Optional[Transform[Color, ColorTransformer]],
    ):
        assert isinstance(interaction.guild, Guild)
        await self.state[interaction.guild].set_guild_log_options(
            interaction,
            channel=channel,
            stacktrace=stacktrace,
            emoji=emoji,
            color=color,
        )

    @cmd_guild.command(
        name="remove",
        description="Remove the error logging configuration for this guild",
    )
    async def cmd_stacktracer_guild_remove(self, interaction: Interaction):
        assert isinstance(interaction.guild, Guild)
        await self.state[interaction.guild].remove_guild_log_options(interaction)
