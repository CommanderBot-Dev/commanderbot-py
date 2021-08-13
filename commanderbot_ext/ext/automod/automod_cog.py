from typing import Optional, cast

from discord import Color, Guild, Message, TextChannel
from discord.ext.commands import Bot, Cog, group

from commanderbot_ext.ext.automod.automod_data import AutomodData
from commanderbot_ext.ext.automod.automod_guild_state import AutomodGuildState
from commanderbot_ext.ext.automod.automod_json_store import AutomodJsonStore
from commanderbot_ext.ext.automod.automod_options import AutomodOptions
from commanderbot_ext.ext.automod.automod_state import AutomodState
from commanderbot_ext.ext.automod.automod_store import AutomodStore
from commanderbot_ext.lib import (
    CogGuildStateManager,
    GuildContext,
    InMemoryDatabaseOptions,
    JsonFileDatabaseAdapter,
    JsonFileDatabaseOptions,
    TextMessage,
    UnsupportedDatabaseOptions,
    checks,
)
from commanderbot_ext.lib.utils import is_bot


def make_automod_store(bot: Bot, cog: Cog, options: AutomodOptions) -> AutomodStore:
    db_options = options.database
    if isinstance(db_options, InMemoryDatabaseOptions):
        return AutomodData()
    if isinstance(db_options, JsonFileDatabaseOptions):
        return AutomodJsonStore(
            bot=bot,
            cog=cog,
            db=JsonFileDatabaseAdapter(
                options=db_options,
                serializer=lambda cache: cache.to_data(),
                deserializer=AutomodData.from_data,
            ),
        )
    raise UnsupportedDatabaseOptions(db_options)


class AutomodCog(Cog, name="commanderbot_ext.ext.automod"):
    """
    Setup rules to perform automated moderator actions.

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
        self.options = AutomodOptions.from_dict(options)
        self.store: AutomodStore = make_automod_store(bot, self, self.options)
        self.state = AutomodState(
            bot=self.bot,
            cog=self,
            guilds=CogGuildStateManager(
                bot=self.bot,
                cog=self,
                factory=lambda guild: AutomodGuildState(
                    bot=bot, cog=self, guild=guild, store=self.store
                ),
            ),
            store=self.store,
        )

    def _guild_state_for_message(self, message: Message) -> Optional[AutomodGuildState]:
        # TODO Can we ignore commands here? #enhance
        if is_bot(self.bot, message.author):
            return
        guild = message.guild
        channel = message.channel
        if isinstance(guild, Guild) and isinstance(channel, TextChannel):
            return self.state[guild]

    # @@ LISTENERS

    @Cog.listener()
    async def on_message(self, message: Message):
        if guild_state := self._guild_state_for_message(message):
            await guild_state.on_message(
                message=cast(TextMessage, message),
            )

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if guild_state := self._guild_state_for_message(after):
            await guild_state.on_message_edit(
                before=cast(TextMessage, before),
                after=cast(TextMessage, after),
            )

    @Cog.listener()
    async def on_message_delete(self, message: Message):
        if guild_state := self._guild_state_for_message(message):
            await guild_state.on_message_delete(
                message=cast(TextMessage, message),
            )

    # IMPL remaining events

    # @@ COMMANDS

    # @@ automod

    @group(
        name="automod",
        brief="Manage automod features.",
        aliases=["am"],
    )
    @checks.guild_only()
    @checks.is_administrator()
    async def cmd_automod(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_automod)

    # @@ automod options

    @cmd_automod.group(
        name="options",
        brief="Configure various automod options.",
    )
    async def cmd_automod_options(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_automod_options)

    @cmd_automod_options.group(
        name="log",
        brief="Configure the default logging behaviour.",
    )
    async def cmd_automod_options_log(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            if ctx.subcommand_passed:
                await ctx.send_help(self.cmd_automod_options)
            else:
                await self.state[ctx.guild].show_default_log_options(ctx)

    @cmd_automod_options_log.command(
        name="set",
        brief="Set the default logging behaviour.",
    )
    async def cmd_automod_options_log_set(
        self,
        ctx: GuildContext,
        channel: TextChannel,
        emoji: Optional[str],
        color: Optional[Color],
    ):
        await self.state[ctx.guild].set_default_log_options(
            ctx,
            channel=channel,
            emoji=emoji,
            color=color,
        )

    @cmd_automod_options_log.command(
        name="remove",
        brief="Remove the default logging behaviour.",
    )
    async def cmd_automod_options_log_remove(self, ctx: GuildContext):
        await self.state[ctx.guild].remove_default_log_options(ctx)

    # @@ automod rules

    @cmd_automod.group(
        name="rules",
        brief="Browse and manage automod rules.",
    )
    async def cmd_automod_rules(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            if ctx.subcommand_passed:
                await ctx.send_help(self.cmd_automod_rules)
            else:
                await self.state[ctx.guild].show_rules(ctx)

    @cmd_automod_rules.command(
        name="show",
        brief="List and show automod rules.",
    )
    async def cmd_automod_rules_show(self, ctx: GuildContext, *, query: str = ""):
        await self.state[ctx.guild].show_rules(ctx, query)

    @cmd_automod_rules.command(
        name="print",
        brief="Print the code of an automod rule.",
    )
    async def cmd_automod_rules_print(self, ctx: GuildContext, *, query: str):
        await self.state[ctx.guild].print_rule(ctx, query)

    @cmd_automod_rules.command(
        name="add",
        brief="Add a new automod rule.",
    )
    async def cmd_automod_rules_add(self, ctx: GuildContext, *, body: str):
        await self.state[ctx.guild].add_rule(ctx, body)

    @cmd_automod_rules.command(
        name="remove",
        brief="Remove an automod rule.",
    )
    async def cmd_automod_rules_remove(self, ctx: GuildContext, name: str):
        await self.state[ctx.guild].remove_rule(ctx, name)

    @cmd_automod_rules.command(
        name="modify",
        brief="Modify an automod rule",
    )
    async def cmd_automod_rules_modify(
        self, ctx: GuildContext, name: str, *, body: str
    ):
        await self.state[ctx.guild].modify_rule(ctx, name, body)

    @cmd_automod_rules.command(
        name="enable",
        brief="Enable an automod rule",
    )
    async def cmd_automod_rules_enable(self, ctx: GuildContext, name: str):
        await self.state[ctx.guild].enable_rule(ctx, name)

    @cmd_automod_rules.command(
        name="disable",
        brief="Disable an automod rule",
    )
    async def cmd_automod_rules_disable(self, ctx: GuildContext, name: str):
        await self.state[ctx.guild].disable_rule(ctx, name)
