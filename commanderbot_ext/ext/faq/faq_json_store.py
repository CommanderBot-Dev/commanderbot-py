from dataclasses import dataclass
from typing import AsyncIterable, List, Optional, Tuple

from discord.guild import Guild

from commanderbot_ext.ext.faq.faq_data import FaqData
from commanderbot_ext.ext.faq.faq_store import FaqEntry
from commanderbot_ext.lib import CogStore, JsonFileDatabaseAdapter


# @implements FaqStore
@dataclass
class FaqJsonStore(CogStore):
    """
    Implementation of `FaqStore` that uses a simple JSON file to persist state.
    """

    db: JsonFileDatabaseAdapter[FaqData]

    # @implements FaqStore
    async def get_faq_entries(self, guild: Guild) -> List[FaqEntry]:
        cache = await self.db.get_cache()
        return await cache.get_faq_entries(guild)

    # @implements FaqStore
    async def require_faq_entry(self, guild: Guild, faq_key: str) -> FaqEntry:
        cache = await self.db.get_cache()
        return await cache.require_faq_entry(guild, faq_key)

    # @implements FaqStore
    async def query_faq_entries(
        self, guild: Guild, faq_query: str
    ) -> AsyncIterable[FaqEntry]:
        cache = await self.db.get_cache()
        async for faq_entry in cache.query_faq_entries(guild, faq_query):
            yield faq_entry

    # @implements FaqStore
    async def scan_for_faqs(self, guild: Guild, text: str) -> Optional[List[FaqEntry]]:
        cache = await self.db.get_cache()
        return await cache.scan_for_faqs(guild, text)

    # @implements FaqStore
    async def increment_faq_hits(self, faq_entry: FaqEntry):
        cache = await self.db.get_cache()
        await cache.increment_faq_hits(faq_entry)
        await self.db.dirty()

    # @implements FaqStore
    async def add_faq(
        self, guild: Guild, faq_key: str, link: str, content: str
    ) -> FaqEntry:
        cache = await self.db.get_cache()
        faq_entry = await cache.add_faq(guild, faq_key, link=link, content=content)
        await self.db.dirty()
        return faq_entry

    # @implements FaqStore
    async def remove_faq(self, guild: Guild, faq_key: str) -> FaqEntry:
        cache = await self.db.get_cache()
        faq_entry = await cache.remove_faq(guild, faq_key)
        await self.db.dirty()
        return faq_entry

    # @implements FaqStore
    async def modify_faq_content(
        self, guild: Guild, faq_key: str, content: str
    ) -> FaqEntry:
        cache = await self.db.get_cache()
        faq_entry = await cache.modify_faq_content(guild, faq_key, content)
        await self.db.dirty()
        return faq_entry

    # @implements FaqStore
    async def modify_faq_link(
        self, guild: Guild, faq_key: str, link: Optional[str]
    ) -> FaqEntry:
        cache = await self.db.get_cache()
        faq_entry = await cache.modify_faq_link(guild, faq_key, link)
        await self.db.dirty()
        return faq_entry

    # @implements FaqStore
    async def modify_faq_aliases(
        self, guild: Guild, faq_key: str, aliases: Tuple[str, ...]
    ) -> FaqEntry:
        cache = await self.db.get_cache()
        faq_entry = await cache.modify_faq_aliases(guild, faq_key, aliases)
        await self.db.dirty()
        return faq_entry

    # @implements FaqStore
    async def modify_faq_tags(
        self, guild: Guild, faq_key: str, tags: Tuple[str, ...]
    ) -> FaqEntry:
        cache = await self.db.get_cache()
        faq_entry = await cache.modify_faq_tags(guild, faq_key, tags)
        await self.db.dirty()
        return faq_entry

    # @implements FaqStore
    async def configure_prefix(self, guild: Guild, prefix: Optional[str]):
        cache = await self.db.get_cache()
        await cache.configure_prefix(guild, prefix)
        await self.db.dirty()

    # @implements FaqStore
    async def configure_match(self, guild: Guild, match: Optional[str]):
        cache = await self.db.get_cache()
        await cache.configure_match(guild, match)
        await self.db.dirty()
