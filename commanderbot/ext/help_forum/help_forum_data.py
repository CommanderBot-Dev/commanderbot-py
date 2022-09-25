from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, DefaultDict, Dict, Optional, Type, TypeVar

from discord import ForumChannel, Guild
from commanderbot.ext.help_forum.help_forum_store import (
    ForumChannelAlreadyRegistered,
    ForumChannelNotRegistered,
)

from commanderbot.lib import (
    ChannelID,
    ForumTagID,
    FromDataMixin,
    GuildID,
    JsonSerializable,
    LogOptions,
)
from commanderbot.lib.utils.utils import dict_without_ellipsis, dict_without_falsies

HF = TypeVar("HF")


@dataclass
class HelpForumForumData(JsonSerializable, FromDataMixin):
    channel_id: ChannelID
    resolved_emoji: str
    unresolved_tag_id: ForumTagID
    resolved_tag_id: ForumTagID

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls: Type[HF], data: Any) -> Optional[HF]:
        if isinstance(data, dict):
            return cls(
                channel_id=data["channel_id"],
                resolved_emoji=data["resolved_emoji"],
                unresolved_tag_id=data["unresolved_tag_id"],
                resolved_tag_id=data["resolved_tag_id"],
            )

    # @implements JsonSerializable
    def to_json(self) -> Any:
        return {
            "channel_id": self.channel_id,
            "resolved_emoji": self.resolved_emoji,
            "unresolved_tag_id": self.unresolved_tag_id,
            "resolved_tag_id": self.resolved_tag_id,
        }


@dataclass
class HelpForumGuildData(JsonSerializable, FromDataMixin):
    log_options: Optional[LogOptions] = None
    help_forums: Dict[ChannelID, HelpForumForumData] = field(default_factory=dict)

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls: Type[HF], data: Any) -> Optional[HF]:
        if isinstance(data, dict):
            log_options = LogOptions.from_field_optional(data, "log")
            help_forums = {}
            for raw_channel_id, raw_forum_data in data.get("forums", {}).items():
                channel_id = int(raw_channel_id)
                help_forums[channel_id] = HelpForumForumData.from_data(raw_forum_data)

            return cls(log_options=log_options, help_forums=help_forums)

    # @implements JsonSerializable
    def to_json(self) -> Any:
        help_forums = {
            str(channel_id): forum_data.to_json()
            for channel_id, forum_data in self.help_forums.items()
        }

        # Omit empty help forums
        trimmed_help_forums = dict_without_falsies(help_forums)

        # Omit empty fields
        data = dict_without_ellipsis(
            log=self.log_options or ...,
            forums=trimmed_help_forums or ...,
        )

        return data

    def is_forum_registered(self, forum_channel: ForumChannel) -> bool:
        return forum_channel.id in self.help_forums

    def _require_help_forum(self, forum_channel: ForumChannel) -> HelpForumForumData:
        # Returns the help forum data if it exists
        if forum := self.help_forums.get(forum_channel.id):
            return forum
        # Otherwise, raise
        raise ForumChannelNotRegistered(forum_channel.name)

    def register_forum_channel(
        self,
        forum_channel: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: ForumTagID,
        resolved_tag: ForumTagID,
    ) -> HelpForumForumData:
        # Check if the forum channel was registered
        if self.is_forum_registered(forum_channel):
            raise ForumChannelAlreadyRegistered(forum_channel.name)

        # Create and add a new help forum
        forum = HelpForumForumData(
            channel_id=forum_channel.id,
            resolved_emoji=resolved_emoji,
            unresolved_tag_id=unresolved_tag,
            resolved_tag_id=resolved_tag,
        )

        self.help_forums[forum_channel.id] = forum

        # Return the newly created help forum
        return forum

    def deregister_forum_channel(
        self, forum_channel: ForumChannel
    ) -> HelpForumForumData:
        # The help forum channel should exist
        forum = self._require_help_forum(forum_channel)
        # Remove it
        del self.help_forums[forum.channel_id]
        # Return it
        return forum

    def get_help_forum_data(
        self, forum_channel: ForumChannel
    ) -> Optional[HelpForumForumData]:
        # Get the full data for a help forum
        return self.help_forums.get(forum_channel.id)

    def get_resolved_emoji(self, forum_channel: ForumChannel) -> Optional[str]:
        # Get the resolved emoji for a help forum
        if forum := self.help_forums.get(forum_channel.id):
            return forum.resolved_emoji

    def get_unresolved_tag_id(
        self, forum_channel: ForumChannel
    ) -> Optional[ForumTagID]:
        # Get the unresolved tag ID for a help forum
        if forum := self.help_forums.get(forum_channel.id):
            return forum.unresolved_tag_id

    def get_resolved_tag_id(self, forum_channel: ForumChannel) -> Optional[ForumTagID]:
        # Get the resolved tag ID for a help forum
        if forum := self.help_forums.get(forum_channel.id):
            return forum.resolved_tag_id

    def modify_resolved_emoji(
        self, forum_channel: ForumChannel, emoji: str
    ) -> HelpForumForumData:
        # Modify resolved emoji for a help forum
        if forum := self._require_help_forum(forum_channel):
            forum.resolved_emoji = emoji
            return forum
        raise ForumChannelNotRegistered(forum_channel.name)

    def modify_unresolved_tag_id(
        self, forum_channel: ForumChannel, tag: ForumTagID
    ) -> HelpForumForumData:
        # Modify unresolved tag ID for a help forum
        if forum := self._require_help_forum(forum_channel):
            forum.unresolved_tag_id = tag
            return forum
        raise ForumChannelNotRegistered(forum_channel.name)

    def modify_resolved_tag_id(
        self, forum_channel: ForumChannel, tag: ForumTagID
    ) -> HelpForumForumData:
        # Modify resolved tag ID for a help forum
        if forum := self._require_help_forum(forum_channel):
            forum.resolved_tag_id = tag
            return forum
        raise ForumChannelNotRegistered(forum_channel.name)

    def set_log_options(
        self, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        # Set the log options for this guild
        old = self.log_options
        self.log_options = log_options
        return old


def _guilds_defaultdict_factory() -> DefaultDict[GuildID, HelpForumGuildData]:
    return defaultdict(lambda: HelpForumGuildData())


@dataclass
class HelpForumData(JsonSerializable, FromDataMixin):
    guilds: DefaultDict[GuildID, HelpForumGuildData] = field(
        default_factory=_guilds_defaultdict_factory
    )

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls: Type[HF], data: Any) -> Optional[HF]:
        if isinstance(data, dict):
            # Construct guild data
            guilds = _guilds_defaultdict_factory()
            for raw_guild_id, raw_guild_data in data.get("guilds", {}).items():
                guild_id = int(raw_guild_id)
                guilds[guild_id] = HelpForumGuildData.from_data(raw_guild_data)

            return cls(guilds=guilds)

    # @implements JsonSerializable
    def to_json(self) -> Any:
        # Omit empty guilds, as well as an empty dict of guilds
        return dict_without_falsies(
            dict_without_falsies(
                guilds={
                    str(guild_id): guild_data.to_json()
                    for guild_id, guild_data in self.guilds.items()
                }
            )
        )

    # @implements HelpForumStore
    async def is_forum_registered(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> bool:
        return self.guilds[guild.id].is_forum_registered(forum_channel)

    # @implements HelpForumStore
    async def register_forum_channel(
        self,
        guild: Guild,
        channel: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: ForumTagID,
        resolved_tag: ForumTagID,
    ) -> HelpForumForumData:
        return self.guilds[guild.id].register_forum_channel(
            channel, resolved_emoji, unresolved_tag, resolved_tag
        )

    # @implements HelpForumStore
    async def deregister_forum_channel(
        self, guild: Guild, channel: ForumChannel
    ) -> HelpForumForumData:
        return self.guilds[guild.id].deregister_forum_channel(channel)

    # @implements HelpForumStore
    async def get_help_forum_data(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> Optional[HelpForumForumData]:
        return self.guilds[guild.id].get_help_forum_data(forum_channel)

    # @implements HelpForumStore
    async def get_resolved_emoji(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> Optional[str]:
        return self.guilds[guild.id].get_resolved_emoji(forum_channel)

    # @implements HelpForumStore
    async def get_unresolved_tag_id(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> Optional[ForumTagID]:
        return self.guilds[guild.id].get_unresolved_tag_id(forum_channel)

    # @implements HelpForumStore
    async def get_resolved_tag_id(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> Optional[ForumTagID]:
        return self.guilds[guild.id].get_resolved_tag_id(forum_channel)

    # @implements HelpForumStore
    async def modify_resolved_emoji(
        self, guild: Guild, forum_channel: ForumChannel, emoji: str
    ) -> HelpForumForumData:
        return self.guilds[guild.id].modify_resolved_emoji(forum_channel, emoji)

    # @implements HelpForumStore
    async def modify_unresolved_tag_id(
        self, guild: Guild, forum_channel: ForumChannel, tag: ForumTagID
    ) -> HelpForumForumData:
        return self.guilds[guild.id].modify_unresolved_tag_id(forum_channel, tag)

    # @implements HelpForumStore
    async def modify_resolved_tag_id(
        self, guild: Guild, forum_channel: ForumChannel, tag: ForumTagID
    ) -> HelpForumForumData:
        return self.guilds[guild.id].modify_resolved_tag_id(forum_channel, tag)

    # @implements HelpForumStore
    async def set_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        return self.guilds[guild.id].set_log_options(log_options)
