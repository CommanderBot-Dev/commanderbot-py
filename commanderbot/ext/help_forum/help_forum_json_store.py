from dataclasses import dataclass
from typing import Optional, Tuple

from discord import ForumChannel, ForumTag, Guild

from commanderbot.ext.help_forum.help_forum_data import HelpForumData
from commanderbot.ext.help_forum.help_forum_store import HelpForum
from commanderbot.lib import CogStore, JsonFileDatabaseAdapter, LogOptions


# @implements HelpForumStore
@dataclass
class HelpForumJsonStore(CogStore):
    """
    Implementation of `HelpForumStore` that uses a simple JSON file to persist state.
    """

    db: JsonFileDatabaseAdapter[HelpForumData]

    # @implements HelpForumStore
    async def require_help_forum(
        self, guild: Guild, channel: ForumChannel
    ) -> HelpForum:
        cache = await self.db.get_cache()
        return await cache.require_help_forum(guild, channel)

    async def get_help_forum(
        self, guild: Guild, channel: ForumChannel
    ) -> Optional[HelpForum]:
        cache = await self.db.get_cache()
        return await cache.get_help_forum(guild, channel)

    # @implements HelpForumStore
    async def register_forum_channel(
        self,
        guild: Guild,
        channel: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: str,
        resolved_tag: str,
    ) -> HelpForum:
        cache = await self.db.get_cache()
        help_forum = await cache.register_forum_channel(
            guild, channel, resolved_emoji, unresolved_tag, resolved_tag
        )
        await self.db.dirty()
        return help_forum

    # @implements HelpForumStore
    async def deregister_forum_channel(
        self, guild: Guild, channel: ForumChannel
    ) -> HelpForum:
        cache = await self.db.get_cache()
        help_forum = await cache.deregister_forum_channel(guild, channel)
        await self.db.dirty()
        return help_forum

    # @implements HelpForumStore
    async def increment_total_threads(self, help_forum: HelpForum):
        cache = await self.db.get_cache()
        await cache.increment_total_threads(help_forum)
        await self.db.dirty()

    # @implements HelpForumStore
    async def increment_resolved_threads(self, help_forum: HelpForum):
        cache = await self.db.get_cache()
        await cache.increment_resolved_threads(help_forum)
        await self.db.dirty()

    # @implements HelpForumStore
    async def modify_resolved_emoji(
        self, guild: Guild, channel: ForumChannel, emoji: str
    ) -> HelpForum:
        cache = await self.db.get_cache()
        help_forum = await cache.modify_resolved_emoji(guild, channel, emoji)
        await self.db.dirty()
        return help_forum

    # @implements HelpForumStore
    async def modify_unresolved_tag(
        self, guild: Guild, channel: ForumChannel, tag: str
    ) -> Tuple[HelpForum, ForumTag]:
        cache = await self.db.get_cache()
        help_forum, new_tag = await cache.modify_unresolved_tag(guild, channel, tag)
        await self.db.dirty()
        return (help_forum, new_tag)

    # @implements HelpForumStore
    async def modify_resolved_tag(
        self, guild: Guild, channel: ForumChannel, tag: str
    ) -> Tuple[HelpForum, ForumTag]:
        cache = await self.db.get_cache()
        help_forum, new_tag = await cache.modify_resolved_tag(guild, channel, tag)
        await self.db.dirty()
        return (help_forum, new_tag)

    # @implements HelpForumStore
    async def get_log_options(self, guild: Guild) -> Optional[LogOptions]:
        cache = await self.db.get_cache()
        return await cache.get_log_options(guild)

    # @implements HelpForumStore
    async def set_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        cache = await self.db.get_cache()
        old_log_options = await cache.set_log_options(guild, log_options)
        await self.db.dirty()
        return old_log_options
