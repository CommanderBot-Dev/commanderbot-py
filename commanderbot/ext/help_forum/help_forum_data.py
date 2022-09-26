import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, DefaultDict, Dict, Optional, Type, TypeVar

from discord import ForumChannel, Guild
from emoji import is_emoji

from commanderbot.ext.help_forum.help_forum_store import (
    ForumChannelAlreadyRegistered,
    ForumChannelNotRegistered,
    HelpForum,
)
from commanderbot.lib import (
    ChannelID,
    ForumTagID,
    FromDataMixin,
    GuildID,
    JsonSerializable,
    LogOptions,
    ResponsiveException,
)
from commanderbot.lib.utils.forums import try_get_tag_from_channel
from commanderbot.lib.utils.utils import dict_without_ellipsis, dict_without_falsies

ST = TypeVar("ST")

CUSTOM_EMOJI_PATTERN = re.compile(r"\<\:\w+\:\d+\>")


class HelpForumInvalidTag(ResponsiveException):
    def __init__(self, channel: ChannelID, tag: str):
        self.channel_id = channel
        self.tag = tag
        super().__init__(
            f"😬 Tag `{self.tag}` does not exist in forum <#{self.channel_id}>"
        )


class HelpForumInvalidEmoji(ResponsiveException):
    def __init__(self, emoji: str):
        self.emoji = emoji
        super().__init__(f"`{emoji}` is not a valid Unicode or Custom emoji")


@dataclass
class HelpForumForumData(JsonSerializable, FromDataMixin):
    channel_id: ChannelID
    resolved_emoji: str
    unresolved_tag_id: ForumTagID
    resolved_tag_id: ForumTagID
    total_threads: int
    resolved_threads: int

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, dict):
            return cls(
                channel_id=data["channel_id"],
                resolved_emoji=data["resolved_emoji"],
                unresolved_tag_id=data["unresolved_tag_id"],
                resolved_tag_id=data["resolved_tag_id"],
                total_threads=data["total_threads"],
                resolved_threads=data["resolved_threads"],
            )

    # @implements JsonSerializable
    def to_json(self) -> Any:
        return {
            "channel_id": self.channel_id,
            "resolved_emoji": self.resolved_emoji,
            "unresolved_tag_id": self.unresolved_tag_id,
            "resolved_tag_id": self.resolved_tag_id,
            "total_threads": self.total_threads,
            "resolved_threads": self.resolved_threads,
        }

    @property
    def resolved_percentage(self) -> float:
        if self.total_threads == 0:
            return 0.0
        return (self.resolved_threads / self.total_threads) * 100


@dataclass
class HelpForumGuildData(JsonSerializable, FromDataMixin):
    log_options: Optional[LogOptions] = None
    help_forums: Dict[ChannelID, HelpForumForumData] = field(default_factory=dict)

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
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

    def is_forum_registered(self, channel: ForumChannel) -> bool:
        return channel.id in self.help_forums

    def _require_help_forum(self, channel: ForumChannel) -> HelpForumForumData:
        # Returns the help forum data if it exists
        if forum := self.help_forums.get(channel.id):
            return forum
        # Otherwise, raise
        raise ForumChannelNotRegistered(channel.id)

    def _is_unicode_or_custom_emoji(self, emoji: str) -> bool:
        return bool(is_emoji(emoji) or CUSTOM_EMOJI_PATTERN.match(emoji))

    def register_forum_channel(
        self,
        channel: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: str,
        resolved_tag: str,
    ) -> HelpForumForumData:
        # Check if the forum channel was registered
        if self.is_forum_registered(channel):
            raise ForumChannelAlreadyRegistered(channel.id)

        # Check if the resolved emoji is valid
        if not self._is_unicode_or_custom_emoji(resolved_emoji):
            raise HelpForumInvalidEmoji(resolved_emoji)

        # Check if the tags exist in the forum channel
        tag_ids: list[ForumTagID] = []
        for tag_str in (unresolved_tag, resolved_tag):
            if tag := try_get_tag_from_channel(channel, tag_str):
                tag_ids.append(tag.id)
            else:
                raise HelpForumInvalidTag(channel.id, tag_str)

        # Create and add a new help forum
        forum = HelpForumForumData(
            channel_id=channel.id,
            resolved_emoji=resolved_emoji,
            unresolved_tag_id=tag_ids[0],
            resolved_tag_id=tag_ids[1],
            total_threads=0,
            resolved_threads=0,
        )

        self.help_forums[channel.id] = forum

        # Return the newly created help forum
        return forum

    def deregister_forum_channel(self, channel: ForumChannel) -> HelpForumForumData:
        # The help forum channel should exist
        forum = self._require_help_forum(channel)
        # Remove it
        del self.help_forums[forum.channel_id]
        # Return it
        return forum

    def try_get_forum(self, channel: ForumChannel) -> HelpForumForumData:
        return self._require_help_forum(channel)

    def get_forum(self, channel: ForumChannel) -> Optional[HelpForumForumData]:
        # Get the help forum if it exists
        return self.help_forums.get(channel.id)

    def modify_resolved_emoji(
        self, channel: ForumChannel, emoji: str
    ) -> HelpForumForumData:
        # Modify resolved emoji for a help forum
        if forum := self._require_help_forum(channel):
            if not self._is_unicode_or_custom_emoji(emoji):
                raise HelpForumInvalidEmoji(emoji)

            forum.resolved_emoji = emoji
            return forum
        raise ForumChannelNotRegistered(channel.id)

    def modify_unresolved_tag_id(
        self, channel: ForumChannel, tag: ForumTagID
    ) -> HelpForumForumData:
        # Modify unresolved tag ID for a help forum
        if forum := self._require_help_forum(channel):
            forum.unresolved_tag_id = tag
            return forum
        raise ForumChannelNotRegistered(channel.id)

    def modify_resolved_tag_id(
        self, channel: ForumChannel, tag: ForumTagID
    ) -> HelpForumForumData:
        # Modify resolved tag ID for a help forum
        if forum := self._require_help_forum(channel):
            forum.resolved_tag_id = tag
            return forum
        raise ForumChannelNotRegistered(channel.id)

    def set_log_options(
        self, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        # Set the log options for this guild
        old = self.log_options
        self.log_options = log_options
        return old


def _guilds_defaultdict_factory() -> DefaultDict[GuildID, HelpForumGuildData]:
    return defaultdict(lambda: HelpForumGuildData())


# @implements HelpForumStore
@dataclass
class HelpForumData(JsonSerializable, FromDataMixin):
    guilds: DefaultDict[GuildID, HelpForumGuildData] = field(
        default_factory=_guilds_defaultdict_factory
    )

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, dict):
            # Construct guild data
            guilds = _guilds_defaultdict_factory()
            for raw_guild_id, raw_guild_data in data.get("guilds", {}).items():
                guild_id = int(raw_guild_id)
                guilds[guild_id] = HelpForumGuildData.from_data(raw_guild_data)

            return cls(guilds=guilds)

    # @implements JsonSerializable
    def to_json(self) -> Any:
        guilds = {
            str(guild_id): guild_data.to_json()
            for guild_id, guild_data in self.guilds.items()
        }

        # Omit empty guild
        trimmed_guilds = dict_without_falsies(guilds)

        # Omit empty fields
        data = dict_without_ellipsis(guilds=trimmed_guilds or ...)

        return data

    # @implements HelpForumStore
    async def is_forum_registered(self, guild: Guild, channel: ForumChannel) -> bool:
        return self.guilds[guild.id].is_forum_registered(channel)

    # @implements HelpForumStore
    async def register_forum_channel(
        self,
        guild: Guild,
        channel: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: str,
        resolved_tag: str,
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
    async def increment_total_threads(self, help_forum: HelpForum):
        help_forum.total_threads += 1

    # @implements HelpForumStore
    async def increment_resolved_threads(self, help_forum: HelpForum):
        help_forum.resolved_threads += 1

    # @implements HelpForumStore
    async def try_get_forum(
        self, guild: Guild, channel: ForumChannel
    ) -> HelpForumForumData:
        return self.guilds[guild.id].try_get_forum(channel)

    # @implements HelpForumStore
    async def get_forum(
        self, guild: Guild, channel: ForumChannel
    ) -> Optional[HelpForumForumData]:
        return self.guilds[guild.id].get_forum(channel)

    # @implements HelpForumStore
    async def modify_resolved_emoji(
        self, guild: Guild, channel: ForumChannel, emoji: str
    ) -> HelpForumForumData:
        return self.guilds[guild.id].modify_resolved_emoji(channel, emoji)

    # @implements HelpForumStore
    async def modify_unresolved_tag_id(
        self, guild: Guild, channel: ForumChannel, tag: ForumTagID
    ) -> HelpForumForumData:
        return self.guilds[guild.id].modify_unresolved_tag_id(channel, tag)

    # @implements HelpForumStore
    async def modify_resolved_tag_id(
        self, guild: Guild, channel: ForumChannel, tag: ForumTagID
    ) -> HelpForumForumData:
        return self.guilds[guild.id].modify_resolved_tag_id(channel, tag)

    # @implements HelpForumStore
    async def set_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        return self.guilds[guild.id].set_log_options(log_options)
