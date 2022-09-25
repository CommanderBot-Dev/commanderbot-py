from dataclasses import dataclass
from typing import Optional

from discord import ForumChannel, Guild

from commanderbot.ext.help_forum.help_forum_data import HelpForumData
from commanderbot.ext.help_forum.help_forum_store import HelpForumForumData
from commanderbot.lib import CogStore, ForumTagID, JsonFileDatabaseAdapter, LogOptions

# @implements HelpForumStore
@dataclass
class HelpForumJsonStore(CogStore):
    """
    Implementation of `HelpForumStore` that uses a simple JSON file to persist state.
    """

    db: JsonFileDatabaseAdapter[HelpForumData]

    async def is_forum_registered(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> bool:
        cache = await self.db.get_cache()
        return await cache.is_forum_registered(guild, forum_channel)

    async def register_forum_channel(
        self,
        guild: Guild,
        forum_channel: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: ForumTagID,
        resolved_tag: ForumTagID,
    ) -> HelpForumForumData:
        cache = await self.db.get_cache()
        help_forum = await cache.register_forum_channel(
            guild, forum_channel, resolved_emoji, unresolved_tag, resolved_tag
        )
        await self.db.dirty()
        return help_forum

    async def deregister_forum_channel(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> HelpForumForumData:
        cache = await self.db.get_cache()
        help_forum = await cache.deregister_forum_channel(guild, forum_channel)
        await self.db.dirty()
        return help_forum

    async def get_help_forum_data(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> Optional[HelpForumForumData]:
        cache = await self.db.get_cache()
        return await cache.get_help_forum_data(guild, forum_channel)

    async def get_resolved_emoji(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> Optional[str]:
        cache = await self.db.get_cache()
        return await cache.get_resolved_emoji(guild, forum_channel)

    async def get_unresolved_tag_id(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> Optional[ForumTagID]:
        cache = await self.db.get_cache()
        return await cache.get_unresolved_tag_id(guild, forum_channel)

    async def get_resolved_tag_id(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> Optional[ForumTagID]:
        cache = await self.db.get_cache()
        return await cache.get_resolved_tag_id(guild, forum_channel)

    async def modify_resolved_emoji(
        self, guild: Guild, forum_channel: ForumChannel, emoji: str
    ) -> HelpForumForumData:
        cache = await self.db.get_cache()
        help_forum = await cache.modify_resolved_emoji(guild, forum_channel, emoji)
        await self.db.dirty()
        return help_forum

    async def modify_unresolved_tag_id(
        self, guild: Guild, forum_channel: ForumChannel, tag: ForumTagID
    ) -> HelpForumForumData:
        cache = await self.db.get_cache()
        help_forum = await cache.modify_unresolved_tag_id(guild, forum_channel, tag)
        await self.db.dirty()
        return help_forum

    async def modify_resolved_tag_id(
        self, guild: Guild, forum_channel: ForumChannel, tag: ForumTagID
    ) -> HelpForumForumData:
        cache = await self.db.get_cache()
        help_forum = await cache.modify_resolved_tag_id(guild, forum_channel, tag)
        await self.db.dirty()
        return help_forum

    async def set_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        cache = await self.db.get_cache()
        old_log_options = await cache.set_log_options(guild, log_options)
        await self.db.dirty()
        return old_log_options
