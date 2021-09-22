from typing import Optional, cast

from discord import Message, TextChannel, Thread
from discord.ext import commands
from discord.ext.commands import Bot, Cog

from commanderbot.ext.faq.faq_data import FaqData
from commanderbot.ext.faq.faq_guild_state import FaqGuildState
from commanderbot.ext.faq.faq_json_store import FaqJsonStore
from commanderbot.ext.faq.faq_options import FaqOptions
from commanderbot.ext.faq.faq_state import FaqState
from commanderbot.ext.faq.faq_store import FaqStore
from commanderbot.lib import (
    CogGuildStateManager,
    GuildContext,
    InMemoryDatabaseOptions,
    JsonFileDatabaseAdapter,
    JsonFileDatabaseOptions,
    TextMessage,
    UnsupportedDatabaseOptions,
    checks,
)
from commanderbot.lib.utils import is_bot


def make_faq_store(bot: Bot, cog: Cog, options: FaqOptions) -> FaqStore:
    db_options = options.database
    if isinstance(db_options, InMemoryDatabaseOptions):
        return FaqData()
    if isinstance(db_options, JsonFileDatabaseOptions):
        return FaqJsonStore(
            bot=bot,
            cog=cog,
            db=JsonFileDatabaseAdapter(
                options=db_options,
                serializer=lambda cache: cache.serialize(),
                deserializer=FaqData.deserialize,
            ),
        )
    raise UnsupportedDatabaseOptions(db_options)


class FaqCog(Cog, name="commanderbot.ext.faq"):
    """
    Allows frequently asked questions (FAQ) to be registered and queried.

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
        self.options = FaqOptions.from_dict(options)
        self.store: FaqStore = make_faq_store(bot, self, self.options)
        self.state = FaqState(
            bot=self.bot,
            cog=self,
            guilds=CogGuildStateManager(
                bot=self.bot,
                cog=self,
                factory=lambda guild: FaqGuildState(
                    bot=bot,
                    cog=self,
                    guild=guild,
                    store=self.store,
                    options=self.options,
                ),
            ),
            store=self.store,
        )

    def _guild_state_for_message(self, message: Message) -> Optional[FaqGuildState]:
        if isinstance(message.channel, TextChannel | Thread) and (
            not is_bot(self.bot, message.author)
        ):
            return self.state[message.channel.guild]

    # @@ LISTENERS

    @Cog.listener()
    async def on_message(self, message: Message):
        if guild_state := self._guild_state_for_message(message):
            await guild_state.on_message(cast(TextMessage, message))

    # @@ COMMANDS

    # @@ faq

    @commands.command(
        name="faq",
        brief="Show a frequently asked question (FAQ).",
    )
    @checks.guild_only()
    async def cmd_faq(self, ctx: GuildContext, *, query: str):
        await self.state[ctx.guild].show_faq(ctx, query)

    # @@ faqs

    @commands.group(
        name="faqs",
        brief="Search and manage FAQs.",
    )
    @checks.guild_only()
    async def cmd_faqs(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            if ctx.subcommand_passed:
                await ctx.send_help(self.cmd_faqs)
            else:
                await self.state[ctx.guild].list_faqs(ctx)

    @cmd_faqs.command(
        name="list",
        brief="List available FAQs.",
    )
    async def cmd_faqs_list(self, ctx: GuildContext):
        await self.state[ctx.guild].list_faqs(ctx)

    @cmd_faqs.command(
        name="search",
        brief="Search through FAQs.",
    )
    async def cmd_faqs_search(self, ctx: GuildContext, *, query: str):
        await self.state[ctx.guild].search_faqs(ctx, query)

    @cmd_faqs.command(
        name="details",
        brief="Show the details of a FAQ.",
    )
    async def cmd_faqs_details(self, ctx: GuildContext, *, name: str):
        await self.state[ctx.guild].show_faq_details(ctx, name)

    # @@ faqs add

    @cmd_faqs.command(
        name="add",
        brief="Add a FAQ.",
    )
    @checks.is_administrator()
    async def cmd_faqs_add(
        self, ctx: GuildContext, key: str, *, message_or_content: str
    ):
        await self.state[ctx.guild].add_faq(ctx, key, message_or_content)

    # @@ faqs remove

    @cmd_faqs.command(
        name="remove",
        brief="Remove a FAQ.",
    )
    @checks.is_administrator()
    async def cmd_faqs_remove(self, ctx: GuildContext, name: str):
        await self.state[ctx.guild].remove_faq(ctx, name)

    # @@ faqs modify

    @cmd_faqs.group(
        name="modify",
        brief="Modify a FAQ.",
    )
    @checks.is_administrator()
    async def cmd_faqs_modify(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_faqs_modify)

    @cmd_faqs_modify.command(
        name="content",
        brief="Modify a FAQ's content.",
    )
    @checks.is_administrator()
    async def cmd_faqs_modify_content(
        self, ctx: GuildContext, name: str, *, message_or_content: str
    ):
        await self.state[ctx.guild].modify_faq_content(ctx, name, message_or_content)

    @cmd_faqs_modify.command(
        name="aliases",
        brief="Modify a FAQ's aliases.",
    )
    @checks.is_administrator()
    async def cmd_faqs_modify_aliases(
        self, ctx: GuildContext, name: str, *aliases: str
    ):
        await self.state[ctx.guild].modify_faq_aliases(ctx, name, aliases)

    @cmd_faqs_modify.command(
        name="tags",
        brief="Modify a FAQ's tags.",
    )
    @checks.is_administrator()
    async def cmd_faqs_modify_tags(self, ctx: GuildContext, name: str, *tags: str):
        await self.state[ctx.guild].modify_faq_tags(ctx, name, tags)

    # @@ faqs options

    @cmd_faqs.group(
        name="options",
        brief="Configure extension options.",
    )
    @checks.is_administrator()
    async def cmd_faqs_options(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_faqs_options)

    # @@ faqs options prefix

    @cmd_faqs_options.group(
        name="prefix",
        brief="Configure the FAQ prefix pattern.",
    )
    async def cmd_faqs_options_prefix(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            if ctx.subcommand_passed:
                await ctx.send_help(self.cmd_faqs_options_prefix)
            else:
                await self.state[ctx.guild].show_prefix_pattern(ctx)

    @cmd_faqs_options_prefix.command(
        name="show",
        brief="Show the FAQ prefix pattern.",
    )
    async def cmd_faqs_options_prefix_show(self, ctx: GuildContext):
        await self.state[ctx.guild].show_prefix_pattern(ctx)

    @cmd_faqs_options_prefix.command(
        name="set",
        brief="Set the FAQ prefix pattern.",
    )
    async def cmd_faqs_options_prefix_set(self, ctx: GuildContext, *, prefix: str):
        await self.state[ctx.guild].set_prefix_pattern(ctx, prefix)

    @cmd_faqs_options_prefix.command(
        name="clear",
        brief="Clear the FAQ prefix pattern.",
    )
    async def cmd_faqs_options_prefix_clear(self, ctx: GuildContext):
        await self.state[ctx.guild].clear_prefix_pattern(ctx)

    # @@ faqs options match

    @cmd_faqs_options.group(
        name="match",
        brief="Configure the FAQ match pattern.",
    )
    async def cmd_faqs_options_match(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            if ctx.subcommand_passed:
                await ctx.send_help(self.cmd_faqs_options_match)
            else:
                await self.state[ctx.guild].show_match_pattern(ctx)

    @cmd_faqs_options_match.command(
        name="show",
        brief="Show the FAQ match pattern.",
    )
    async def cmd_faqs_options_match_show(self, ctx: GuildContext):
        await self.state[ctx.guild].show_match_pattern(ctx)

    @cmd_faqs_options_match.command(
        name="set",
        brief="Set the FAQ match pattern.",
    )
    async def cmd_faqs_options_match_set(self, ctx: GuildContext, *, match: str):
        await self.state[ctx.guild].set_match_pattern(ctx, match)

    @cmd_faqs_options_match.command(
        name="clear",
        brief="Clear the FAQ match pattern.",
    )
    async def cmd_faqs_options_match_clear(self, ctx: GuildContext):
        await self.state[ctx.guild].clear_match_pattern(ctx)
