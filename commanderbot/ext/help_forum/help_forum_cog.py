from discord import (
    ForumChannel,
    Guild,
    Interaction,
    Message,
    RawReactionActionEvent,
    RawThreadUpdateEvent,
    Thread,
)
from discord.app_commands import (
    Group,
    Transform,
    command,
    default_permissions,
    describe,
    guild_only,
)
from discord.ext.commands import Bot, Cog, GroupCog

from commanderbot.ext.help_forum.help_forum_data import HelpForumData
from commanderbot.ext.help_forum.help_forum_guild_state import HelpForumGuildState
from commanderbot.ext.help_forum.help_forum_json_store import HelpForumJsonStore
from commanderbot.ext.help_forum.help_forum_options import HelpForumOptions
from commanderbot.ext.help_forum.help_forum_state import HelpForumState
from commanderbot.ext.help_forum.help_forum_store import HelpForumStore
from commanderbot.lib import (
    CogGuildStateManager,
    InMemoryDatabaseOptions,
    JsonFileDatabaseAdapter,
    JsonFileDatabaseOptions,
    UnsupportedDatabaseOptions,
)
from commanderbot.lib.interactions import EmojiTransformer
from commanderbot.lib.utils import is_bot


def _make_store(bot: Bot, cog: Cog, options: HelpForumOptions) -> HelpForumStore:
    db_options = options.database
    if isinstance(db_options, InMemoryDatabaseOptions):
        return HelpForumData()
    if isinstance(db_options, JsonFileDatabaseOptions):
        return HelpForumJsonStore(
            bot=bot,
            cog=cog,
            db=JsonFileDatabaseAdapter(
                options=db_options,
                serializer=lambda cache: cache.to_json(),
                deserializer=HelpForumData.from_data,
            ),
        )
    raise UnsupportedDatabaseOptions(db_options)


@guild_only()
@default_permissions(manage_channels=True)
class HelpForumCog(
    GroupCog,
    name="commanderbot.ext.help_forum",
    group_name="forum",
    group_description="Manage help forums",
):
    def __init__(self, bot: Bot, **options):
        self.bot: Bot = bot
        self.options = HelpForumOptions.from_data(options)
        self.store: HelpForumStore = _make_store(self.bot, self, self.options)
        self.state = HelpForumState(
            bot=self.bot,
            cog=self,
            guilds=CogGuildStateManager(
                bot=self.bot,
                cog=self,
                factory=lambda guild: HelpForumGuildState(
                    bot=self.bot, cog=self, guild=guild, store=self.store
                ),
            ),
            store=self.store,
        )

    # @@ LISTENERS

    @Cog.listener()
    async def on_thread_create(self, thread: Thread):
        await self.state[thread.guild].on_thread_create(thread)

    @Cog.listener()
    async def on_raw_thread_update(self, payload: RawThreadUpdateEvent):
        await self.state[payload.guild_id].on_raw_thread_update(payload)

    @Cog.listener()
    async def on_message(self, message: Message):
        if not is_bot(self.bot, message.author) and isinstance(message.channel, Thread):
            await self.state[message.channel.guild].on_message(message)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        guild = payload.guild_id
        member = payload.member
        if guild and member and (not is_bot(self.bot, member)):
            await self.state[guild].on_raw_reaction_add(payload)

    # @@ COMMANDS

    # groups
    cmd_forum_modify = Group(name="modify", description="Modify help forums")

    # @@ forum register/deregister/details

    @command(name="register", description="Register a forum channel as a help forum")
    @describe(
        channel="The forum channel to register",
        resolved_emoji="The emoji that's used for resolving threads",
        unresolved_tag="The tag for unresolved threads",
        resolved_tag="The tag for resolved threads",
    )
    async def cmd_forum_register(
        self,
        interaction: Interaction,
        channel: ForumChannel,
        resolved_emoji: Transform[str, EmojiTransformer],
        unresolved_tag: str,
        resolved_tag: str,
    ):
        assert isinstance(interaction.guild, Guild)
        await self.state[interaction.guild].register_forum_channel(
            interaction, channel, resolved_emoji, unresolved_tag, resolved_tag
        )

    @command(
        name="deregister", description="Deregister a forum channel as a help forum"
    )
    @describe(channel="The forum channel to register")
    async def cmd_forum_deregister(
        self, interaction: Interaction, channel: ForumChannel
    ):
        assert isinstance(interaction.guild, Guild)
        await self.state[interaction.guild].deregister_forum_channel(
            interaction, channel
        )

    @command(name="details", description="Show the details of a forum")
    @describe(channel="The channel to show details about")
    async def cmd_forum_details(self, interaction: Interaction, channel: ForumChannel):
        assert isinstance(interaction.guild, Guild)
        await self.state[interaction.guild].details(interaction, channel)

    # @@ forum modify

    @cmd_forum_modify.command(
        name="resolved-emoji", description="Modify the resolved emoji for a help forum"
    )
    @describe(channel="The channel to modify", emoji="The new emoji")
    async def cmd_forum_modify_resolved_emoji(
        self,
        interaction: Interaction,
        channel: ForumChannel,
        emoji: Transform[str, EmojiTransformer],
    ):
        assert isinstance(interaction.guild, Guild)
        await self.state[interaction.guild].modify_resolved_emoji(
            interaction, channel, emoji
        )

    @cmd_forum_modify.command(
        name="unresolved-tag", description="Modify the unresolved tag for a help forum"
    )
    @describe(channel="The channel to modify", tag="ID or name of the new tag")
    async def cmd_forum_modify_unresolved_tag(
        self, interaction: Interaction, channel: ForumChannel, tag: str
    ):
        assert isinstance(interaction.guild, Guild)
        await self.state[interaction.guild].modify_unresolved_tag(
            interaction, channel, tag
        )

    @cmd_forum_modify.command(
        name="resolved-tag", description="Modify the resolved tag for a help forum"
    )
    @describe(channel="The channel to modify", tag="ID or name of the new tag")
    async def cmd_forum_modify_resolved_tag(
        self, interaction: Interaction, channel: ForumChannel, tag: str
    ):
        assert isinstance(interaction.guild, Guild)
        await self.state[interaction.guild].modify_resolved_tag(
            interaction, channel, tag
        )
