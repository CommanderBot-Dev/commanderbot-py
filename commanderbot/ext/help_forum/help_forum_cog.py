from discord import ForumChannel, ForumTag, Guild, Interaction, Permissions
from discord.app_commands import Group, describe
from discord.ext.commands import Bot, Cog

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


class HelpForumCog(Cog, name="commanderbot.ext.help_forum"):
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

    def _format_tag_name(self, tag: ForumTag):
        formatted_emoji = f"{tag.emoji} " if tag.emoji else ""
        return f"{formatted_emoji}{tag.name} ID={tag.id}"

    # @@ COMMANDS

    # groups
    cmd_forum = Group(
        name="forum",
        description="Manage help forums",
        guild_only=True,
        default_permissions=Permissions(manage_channels=True),
    )

    cmd_forum_modify = Group(
        name="modify", description="Modify help forums", parent=cmd_forum
    )

    # @@ forum register/deregister/details

    @cmd_forum.command(
        name="register", description="Register a forum channel as a help forum"
    )
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
        resolved_emoji: str,
        unresolved_tag: str,
        resolved_tag: str,
    ):
        assert isinstance(interaction.guild, Guild)
        await self.state[interaction.guild].register_forum_channel(
            interaction, channel, resolved_emoji, unresolved_tag, resolved_tag
        )

    @cmd_forum.command(
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

    @cmd_forum.command(name="details", description="Show the details of a forum")
    @describe(channel="The channel to show details about")
    async def cmd_forum_details(self, interaction: Interaction, channel: ForumChannel):
        assert isinstance(interaction.guild, Guild)
        await self.state[interaction.guild].details(interaction, channel)

    # @@ forum query

    @cmd_forum.command(name="query", description="Query forum channel tags")
    @describe(channel="The forum channel to query")
    async def cmd_forum_query(self, interaction: Interaction, channel: ForumChannel):
        assert isinstance(interaction.guild, Guild)

        # Build message
        message = "\n".join(
            (
                f"Tags for <#{channel.id}>",
                "```py",
                *(self._format_tag_name(tag) for tag in channel.available_tags),
                "```",
            )
        )

        # Send response
        await interaction.response.send_message(message)

    # @@ forum modify

    @cmd_forum_modify.command(name="resolved-emoji", description="Modify the resolved emoji for a help forum")
    @describe(channel="The channel to modify", emoji="The new emoji")
    async def cmd_forum_modify_resolved_emoji(self, interaction: Interaction, channel: ForumChannel, emoji: str):
        assert isinstance(interaction.guild, Guild)
        await self.state[interaction.guild].modify_resolved_emoji(interaction, channel, emoji)
