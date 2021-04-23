from typing import Optional, cast

from discord import Guild, Message, TextChannel
from discord.ext.commands import Bot, Cog, MessageConverter, command, group

from commanderbot_ext.ext.faq.faq_data import FaqData
from commanderbot_ext.ext.faq.faq_guild_state import FaqGuildState
from commanderbot_ext.ext.faq.faq_json_store import FaqJsonStore
from commanderbot_ext.ext.faq.faq_options import FaqOptions
from commanderbot_ext.ext.faq.faq_state import FaqState
from commanderbot_ext.ext.faq.faq_store import FaqStore
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


class FaqCog(Cog, name="commanderbot_ext.ext.faq"):
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
                    bot=bot, cog=self, guild=guild, store=self.store
                ),
            ),
            store=self.store,
        )

    # @@ LISTENERS

    @Cog.listener()
    async def on_message(self, message: Message):
        if is_bot(self.bot, message.author):
            return
        guild = message.guild
        channel = message.channel
        if isinstance(guild, Guild) and isinstance(channel, TextChannel):
            await self.state[guild].on_message(cast(TextMessage, message))

    # @@ COMMANDS

    # @@ faq

    @command(
        name="faq",
        brief="Show or list all FAQs.",
    )
    @checks.guild_only()
    async def cmd_faq(self, ctx: GuildContext, *, faq_query: Optional[str]):
        if faq_query:
            await self.state[ctx.guild].show_faq(ctx, faq_query)
        else:
            await self.state[ctx.guild].list_faqs(ctx)

    # @@ faqs

    @group(
        name="faqs",
        brief="Manage FAQs, or list all FAQs.",
    )
    @checks.guild_only()
    async def cmd_faqs(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            if ctx.subcommand_passed:
                await ctx.send_help(self.cmd_faqs)
            else:
                await self.state[ctx.guild].list_faqs(ctx)

    @cmd_faqs.command(
        name="details",
        brief="Show the details of FAQs.",
    )
    async def cmd_faqs_details(self, ctx: GuildContext, *, faq_query: str):
        await self.state[ctx.guild].show_faq_details(ctx, faq_query)

    # @@ faqs add

    @cmd_faqs.command(
        name="add",
        brief="Add a FAQ.",
    )
    @checks.is_administrator()
    async def cmd_faqs_add(
        self, ctx: GuildContext, faq_key: str, *, message_or_content: str
    ):
        try:
            message = await MessageConverter().convert(ctx, message_or_content)
            assert isinstance(message, Message)
            content = message.content
            assert isinstance(content, str)
        except:
            message = ctx.message
            assert isinstance(message, Message)
            content = message_or_content
        await self.state[ctx.guild].add_faq(
            ctx,
            faq_key,
            link=message.jump_url,
            content=content,
        )

    # @@ faqs remove

    @cmd_faqs.command(
        name="remove",
        brief="Remove a FAQ.",
    )
    @checks.is_administrator()
    async def cmd_faqs_remove(self, ctx: GuildContext, faq_key: str):
        await self.state[ctx.guild].remove_faq(ctx, faq_key)

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
        self, ctx: GuildContext, faq_key: str, content: str
    ):
        await self.state[ctx.guild].modify_faq_content(ctx, faq_key, content)

    @cmd_faqs_modify.command(
        name="link",
        brief="Modify a FAQ's link.",
    )
    @checks.is_administrator()
    async def cmd_faqs_modify_link(
        self, ctx: GuildContext, faq_key: str, link: Optional[str]
    ):
        await self.state[ctx.guild].modify_faq_link(ctx, faq_key, link)

    @cmd_faqs_modify.command(
        name="aliases",
        brief="Modify a FAQ's aliases.",
    )
    @checks.is_administrator()
    async def cmd_faqs_modify_aliases(
        self, ctx: GuildContext, faq_key: str, *aliases: str
    ):
        await self.state[ctx.guild].modify_faq_aliases(ctx, faq_key, aliases)

    @cmd_faqs_modify.command(
        name="tags",
        brief="Modify a FAQ's tags.",
    )
    @checks.is_administrator()
    async def cmd_faqs_modify_tags(self, ctx: GuildContext, faq_key: str, *tags: str):
        await self.state[ctx.guild].modify_faq_tags(ctx, faq_key, tags)

    # @@ faqs configure

    @cmd_faqs.group(
        name="configure",
        aliases=["cfg"],
        brief="Configure FAQ settings.",
    )
    @checks.is_administrator()
    async def cmd_faqs_configure(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_faqs_configure)

    @cmd_faqs_configure.command(
        name="prefix",
        brief="Configure FAQ prefix.",
    )
    async def cmd_faqs_configure_prefix(
        self, ctx: GuildContext, *, prefix: Optional[str] = None
    ):
        await self.state[ctx.guild].configure_prefix(ctx, prefix)

    @cmd_faqs_configure.command(
        name="match",
        brief="Configure FAQ match pattern.",
    )
    async def cmd_faqs_configure_match(
        self, ctx: GuildContext, *, match: Optional[str] = None
    ):
        await self.state[ctx.guild].configure_match(ctx, match)
