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
from commanderbot.lib.forums import require_tag
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

    def _is_forum_registered(self, forum: ForumChannel):
        return forum.id in self.help_forums.keys()

    def _require_tag(self, forum: ForumChannel, tag_str: str) -> ForumTag:
        # Returns the forum tag if it exists
        # This is just a wrapper around our library function so we can throw a custom exception
        try:
            return require_tag(forum, tag_str)
        except:
            raise HelpForumInvalidTag(forum.id, tag_str)

    def require_help_forum(self, forum: ForumChannel) -> HelpForumForumData:
        # Returns the help forum data if it exists
        if forum_data := self.help_forums.get(forum.id):
            return forum_data
        # Otherwise, raise
        raise ForumChannelNotRegistered(forum.id)

    def get_help_forum(self, forum: ForumChannel) -> Optional[HelpForumForumData]:
        return self.help_forums.get(forum.id)

    def register_forum_channel(
        self,
        forum: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: str,
        resolved_tag: str,
    ) -> HelpForumForumData:
        # Check if the forum channel was already registered
        if self._is_forum_registered(forum):
            raise ForumChannelAlreadyRegistered(forum.id)

        # Check if the tags exist in the forum channel
        valid_unresolved_tag: ForumTag = self._require_tag(forum, unresolved_tag)
        valid_resolved_tag: ForumTag = self._require_tag(forum, resolved_tag)

        # Create and add a new help forum
        forum_data = HelpForumForumData(
            channel_id=forum.id,
            resolved_emoji=resolved_emoji,
            unresolved_tag_id=valid_unresolved_tag.id,
            resolved_tag_id=valid_resolved_tag.id,
            threads_created=0,
            resolutions=0,
        )

        self.help_forums[forum.id] = forum_data

        # Return the newly created help forum
        return forum_data

    def deregister_forum_channel(self, forum: ForumChannel) -> HelpForumForumData:
        # The help forum channel should exist
        forum_data = self.require_help_forum(forum)
        # Remove it
        del self.help_forums[forum_data.channel_id]
        # Return it
        return forum_data

    def modify_resolved_emoji(
        self, forum: ForumChannel, emoji: str
    ) -> HelpForumForumData:
        # Modify resolved emoji for a help forum
        forum_data = self.require_help_forum(forum)
        forum_data.resolved_emoji = emoji
        return forum_data

    def modify_unresolved_tag(
        self, forum: ForumChannel, tag: str
    ) -> Tuple[HelpForumForumData, ForumTag]:
        # Modify unresolved tag ID for a help forum
        forum_data = self.require_help_forum(forum)
        valid_tag = self._require_tag(forum, tag)
        forum_data.unresolved_tag_id = valid_tag.id
        return (forum_data, valid_tag)

    def modify_resolved_tag(
        self, forum: ForumChannel, tag: str
    ) -> Tuple[HelpForumForumData, ForumTag]:
        # Modify resolved tag ID for a help forum
        forum_data = self.require_help_forum(forum)
        valid_tag = self._require_tag(forum, tag)
        forum_data.resolved_tag_id = valid_tag.id
        return (forum_data, valid_tag)


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
    async def require_help_forum(self, guild: Guild, forum: ForumChannel) -> HelpForum:
        return self.guilds[guild.id].require_help_forum(forum)

    # @implements HelpForumStore
    async def get_help_forum(
        self, guild: Guild, forum: ForumChannel
    ) -> Optional[HelpForum]:
        return self.guilds[guild.id].get_help_forum(forum)

    # @implements HelpForumStore
    async def register_forum_channel(
        self,
        guild: Guild,
        forum: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: str,
        resolved_tag: str,
    ) -> HelpForum:
        return self.guilds[guild.id].register_forum_channel(
            forum, resolved_emoji, unresolved_tag, resolved_tag
        )

    # @implements HelpForumStore
    async def deregister_forum_channel(
        self, guild: Guild, forum: ForumChannel
    ) -> HelpForum:
        return self.guilds[guild.id].deregister_forum_channel(forum)

    # @implements HelpForumStore
    async def increment_threads_created(self, help_forum: HelpForum):
        help_forum.threads_created += 1

    # @implements HelpForumStore
    async def increment_resolutions(self, help_forum: HelpForum):
        help_forum.resolutions += 1

    # @implements HelpForumStore
    async def modify_resolved_emoji(
        self, guild: Guild, forum: ForumChannel, emoji: str
    ) -> HelpForum:
        return self.guilds[guild.id].modify_resolved_emoji(forum, emoji)

    # @implements HelpForumStore
    async def modify_unresolved_tag(
        self, guild: Guild, forum: ForumChannel, tag: str
    ) -> Tuple[HelpForum, ForumTag]:
        return self.guilds[guild.id].modify_unresolved_tag(forum, tag)

    # @implements HelpForumStore
    async def modify_resolved_tag(
        self, guild: Guild, forum: ForumChannel, tag: str
    ) -> Tuple[HelpForum, ForumTag]:
        return self.guilds[guild.id].modify_resolved_tag(forum, tag)
