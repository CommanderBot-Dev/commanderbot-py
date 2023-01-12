import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, DefaultDict, Dict, Optional, Tuple, Type, TypeVar

from discord import ForumChannel, ForumTag, Guild, PartialEmoji

from commanderbot.ext.help_forum.help_forum_exceptions import (
    ForumChannelAlreadyRegistered,
    ForumChannelNotRegistered,
    HelpForumInvalidTag,
)
from commanderbot.ext.help_forum.help_forum_store import HelpForum
from commanderbot.lib import (
    ChannelID,
    ForumTagID,
    FromDataMixin,
    GuildID,
    JsonSerializable,
)
from commanderbot.lib.forums import try_get_tag
from commanderbot.lib.utils.utils import dict_without_ellipsis, dict_without_falsies

ST = TypeVar("ST")


@dataclass
class HelpForumForumData(JsonSerializable, FromDataMixin):
    channel_id: ChannelID
    resolved_emoji: str
    unresolved_tag_id: ForumTagID
    resolved_tag_id: ForumTagID
    threads_created: int
    resolutions: int

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, dict):
            return cls(
                channel_id=data["channel_id"],
                resolved_emoji=data["resolved_emoji"],
                unresolved_tag_id=data["unresolved_tag_id"],
                resolved_tag_id=data["resolved_tag_id"],
                threads_created=data["threads_created"],
                resolutions=data["resolutions"],
            )

    # @implements JsonSerializable
    def to_json(self) -> Any:
        return {
            "channel_id": self.channel_id,
            "resolved_emoji": self.resolved_emoji,
            "unresolved_tag_id": self.unresolved_tag_id,
            "resolved_tag_id": self.resolved_tag_id,
            "threads_created": self.threads_created,
            "resolutions": self.resolutions,
        }

    @property
    def partial_resolved_emoji(self) -> PartialEmoji:
        return PartialEmoji.from_str(self.resolved_emoji)

    @property
    def thread_state_tags(self) -> tuple[ForumTagID, ForumTagID]:
        return (self.unresolved_tag_id, self.resolved_tag_id)

    @property
    def ratio(self) -> tuple[int, int]:
        if self.threads_created == 0 or self.resolutions == 0:
            return (self.threads_created, self.resolutions)

        gcd: int = math.gcd(self.threads_created, self.resolutions)
        return (self.threads_created // gcd, self.resolutions // gcd)


@dataclass
class HelpForumGuildData(JsonSerializable, FromDataMixin):
    help_forums: Dict[ChannelID, HelpForumForumData] = field(default_factory=dict)

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, dict):
            help_forums = {}
            for raw_channel_id, raw_forum_data in data.get("help_forums", {}).items():
                channel_id = int(raw_channel_id)
                help_forums[channel_id] = HelpForumForumData.from_data(raw_forum_data)

            return cls(help_forums=help_forums)

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
            help_forums=trimmed_help_forums or ...,
        )

        return data

    def _is_forum_registered(self, channel: ForumChannel):
        return channel.id in self.help_forums.keys()

    def _require_tag(self, channel: ForumChannel, tag: str) -> ForumTag:
        if found_tag := try_get_tag(channel, tag, case_sensitive=False):
            return found_tag
        raise HelpForumInvalidTag(channel.id, tag)

    def require_help_forum(self, channel: ForumChannel) -> HelpForumForumData:
        # Returns the help forum data if it exists
        if forum := self.help_forums.get(channel.id):
            return forum
        # Otherwise, raise
        raise ForumChannelNotRegistered(channel.id)

    def get_help_forum(self, channel: ForumChannel) -> Optional[HelpForumForumData]:
        return self.help_forums.get(channel.id)

    def register_forum_channel(
        self,
        channel: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: str,
        resolved_tag: str,
    ) -> HelpForumForumData:
        # Check if the forum channel was already registered
        if self._is_forum_registered(channel):
            raise ForumChannelAlreadyRegistered(channel.id)

        # Check if the tags exist in the forum channel
        valid_unresolved_tag: ForumTag = self._require_tag(channel, unresolved_tag)
        valid_resolved_tag: ForumTag = self._require_tag(channel, resolved_tag)

        # Create and add a new help forum
        forum = HelpForumForumData(
            channel_id=channel.id,
            resolved_emoji=resolved_emoji,
            unresolved_tag_id=valid_unresolved_tag.id,
            resolved_tag_id=valid_resolved_tag.id,
            threads_created=0,
            resolutions=0,
        )

        self.help_forums[channel.id] = forum

        # Return the newly created help forum
        return forum

    def deregister_forum_channel(self, channel: ForumChannel) -> HelpForumForumData:
        # The help forum channel should exist
        forum = self.require_help_forum(channel)
        # Remove it
        del self.help_forums[forum.channel_id]
        # Return it
        return forum

    def modify_resolved_emoji(
        self, channel: ForumChannel, emoji: str
    ) -> HelpForumForumData:
        # Modify resolved emoji for a help forum
        if forum := self.require_help_forum(channel):
            forum.resolved_emoji = emoji
            return forum
        raise ForumChannelNotRegistered(channel.id)

    def modify_unresolved_tag(
        self, channel: ForumChannel, tag: str
    ) -> Tuple[HelpForumForumData, ForumTag]:
        # Modify unresolved tag ID for a help forum
        forum = self.require_help_forum(channel)
        valid_tag = self._require_tag(channel, tag)
        forum.unresolved_tag_id = valid_tag.id
        return (forum, valid_tag)

    def modify_resolved_tag(
        self, channel: ForumChannel, tag: str
    ) -> Tuple[HelpForumForumData, ForumTag]:
        # Modify resolved tag ID for a help forum
        forum = self.require_help_forum(channel)
        valid_tag = self._require_tag(channel, tag)
        forum.resolved_tag_id = valid_tag.id
        return (forum, valid_tag)


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

        # Omit empty guilds
        trimmed_guilds = dict_without_falsies(guilds)

        # Omit empty fields
        data = dict_without_ellipsis(guilds=trimmed_guilds or ...)

        return data

    # @implements HelpForumStore
    async def require_help_forum(
        self, guild: Guild, channel: ForumChannel
    ) -> HelpForum:
        return self.guilds[guild.id].require_help_forum(channel)

    # @implements HelpForumStore
    async def get_help_forum(
        self, guild: Guild, channel: ForumChannel
    ) -> Optional[HelpForum]:
        return self.guilds[guild.id].get_help_forum(channel)

    # @implements HelpForumStore
    async def register_forum_channel(
        self,
        guild: Guild,
        channel: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: str,
        resolved_tag: str,
    ) -> HelpForum:
        return self.guilds[guild.id].register_forum_channel(
            channel, resolved_emoji, unresolved_tag, resolved_tag
        )

    # @implements HelpForumStore
    async def deregister_forum_channel(
        self, guild: Guild, channel: ForumChannel
    ) -> HelpForum:
        return self.guilds[guild.id].deregister_forum_channel(channel)

    # @implements HelpForumStore
    async def increment_threads_created(self, help_forum: HelpForum):
        help_forum.threads_created += 1

    # @implements HelpForumStore
    async def increment_resolutions(self, help_forum: HelpForum):
        help_forum.resolutions += 1

    # @implements HelpForumStore
    async def modify_resolved_emoji(
        self, guild: Guild, channel: ForumChannel, emoji: str
    ) -> HelpForum:
        return self.guilds[guild.id].modify_resolved_emoji(channel, emoji)

    # @implements HelpForumStore
    async def modify_unresolved_tag(
        self, guild: Guild, channel: ForumChannel, tag: str
    ) -> Tuple[HelpForum, ForumTag]:
        return self.guilds[guild.id].modify_unresolved_tag(channel, tag)

    # @implements HelpForumStore
    async def modify_resolved_tag(
        self, guild: Guild, channel: ForumChannel, tag: str
    ) -> Tuple[HelpForum, ForumTag]:
        return self.guilds[guild.id].modify_resolved_tag(channel, tag)
