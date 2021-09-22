import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from discord import Guild

from commanderbot.ext.faq.faq_data import FaqData
from commanderbot.ext.faq.faq_store import FaqEntry
from commanderbot.lib import CogStore, JsonFileDatabaseAdapter


# @implements FaqStore
@dataclass
class FaqJsonStore(CogStore):
    """
    Implementation of `FaqStore` that uses a simple JSON file to persist state.
    """

    db: JsonFileDatabaseAdapter[FaqData]

    # @implements FaqStore
    async def get_prefix_pattern(self, guild: Guild) -> Optional[re.Pattern]:
        cache = await self.db.get_cache()
        return await cache.get_prefix_pattern(guild)

    # @implements FaqStore
    async def set_prefix_pattern(
        self, guild: Guild, prefix: Optional[str]
    ) -> Optional[re.Pattern]:
        cache = await self.db.get_cache()
        result = await cache.set_prefix_pattern(guild, prefix)
        await self.db.dirty()
        return result

    # @implements FaqStore
    async def get_match_pattern(self, guild: Guild) -> Optional[re.Pattern]:
        cache = await self.db.get_cache()
        return await cache.get_match_pattern(guild)

    # @implements FaqStore
    async def set_match_pattern(
        self, guild: Guild, match: Optional[str]
    ) -> Optional[re.Pattern]:
        cache = await self.db.get_cache()
        result = await cache.set_match_pattern(guild, match)
        await self.db.dirty()
        return result

    # @implements FaqStore
    async def get_faq_by_name(self, guild: Guild, name: str) -> Optional[FaqEntry]:
        cache = await self.db.get_cache()
        return await cache.get_faq_by_name(guild, name)

    # @implements FaqStore
    async def require_faq_by_name(self, guild: Guild, name: str) -> FaqEntry:
        cache = await self.db.get_cache()
        return await cache.require_faq_by_name(guild, name)

    # @implements FaqStore
    async def get_all_faqs(self, guild: Guild) -> List[FaqEntry]:
        cache = await self.db.get_cache()
        return await cache.get_all_faqs(guild)

    # @implements FaqStore
    async def get_faqs_by_query(
        self, guild: Guild, query: str, cap: int
    ) -> List[FaqEntry]:
        cache = await self.db.get_cache()
        return await cache.get_faqs_by_query(guild, query, cap)

    # @implements FaqStore
    async def get_faqs_by_match(
        self, guild: Guild, content: str, cap: int
    ) -> List[FaqEntry]:
        cache = await self.db.get_cache()
        return await cache.get_faqs_by_match(guild, content, cap)

    # @implements FaqStore
    async def increment_faq_hits(self, faq: FaqEntry):
        cache = await self.db.get_cache()
        await cache.increment_faq_hits(faq)
        await self.db.dirty()

    # @implements FaqStore
    async def add_faq(
        self, guild: Guild, key: str, link: str, content: str
    ) -> FaqEntry:
        cache = await self.db.get_cache()
        faq = await cache.add_faq(guild, key, link=link, content=content)
        await self.db.dirty()
        return faq

    # @implements FaqStore
    async def remove_faq(self, guild: Guild, name: str) -> FaqEntry:
        cache = await self.db.get_cache()
        faq = await cache.remove_faq(guild, name)
        await self.db.dirty()
        return faq

    # @implements FaqStore
    async def modify_faq_content(
        self, guild: Guild, name: str, link: str, content: str
    ) -> FaqEntry:
        cache = await self.db.get_cache()
        faq = await cache.modify_faq_content(guild, name, link=link, content=content)
        await self.db.dirty()
        return faq

    # @implements FaqStore
    async def modify_faq_aliases(
        self, guild: Guild, name: str, aliases: Tuple[str, ...]
    ) -> FaqEntry:
        cache = await self.db.get_cache()
        faq = await cache.modify_faq_aliases(guild, name, aliases)
        await self.db.dirty()
        return faq

    # @implements FaqStore
    async def modify_faq_tags(
        self, guild: Guild, name: str, tags: Tuple[str, ...]
    ) -> FaqEntry:
        cache = await self.db.get_cache()
        faq = await cache.modify_faq_tags(guild, name, tags)
        await self.db.dirty()
        return faq
