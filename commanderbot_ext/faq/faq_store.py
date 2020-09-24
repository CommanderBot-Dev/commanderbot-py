from typing import Iterable, Optional

from commanderbot_ext.faq.faq_cache import FaqCache, FaqEntry, FaqGuildData
from commanderbot_ext.faq.faq_options import FaqOptions
from commanderbot_lib.database.abc.dict_database import DictDatabase
from commanderbot_lib.store.abc.cached_store import CachedStore
from discord import Guild


class FaqStore(CachedStore[FaqOptions, DictDatabase, FaqCache]):
    # @implements CachedStore
    async def _build_cache(self, data: dict) -> FaqCache:
        return await FaqCache.deserialize(data)

    # @implements CachedStore
    async def serialize(self) -> dict:
        return self._cache.serialize()

    def get_guild_data(self, guild: Guild) -> Optional[FaqGuildData]:
        return self._cache.guilds.get(guild.id)

    async def iter_guild_faqs(self, guild: Guild) -> Optional[Iterable[FaqEntry]]:
        if guild_data := self.get_guild_data(guild):
            return guild_data.entries.values()

    async def get_guild_faq(self, guild: Guild, faq_name: str) -> Optional[FaqEntry]:
        if guild_data := self.get_guild_data(guild):
            return guild_data.entries.get(faq_name)

    async def add_guild_faq(self, guild: Guild, faq_entry: FaqEntry):
        guild_data = self.get_guild_data(guild)
        if guild_data is None:
            guild_data = FaqGuildData(guild_id=guild.id, entries={})
            self._cache.guilds[guild.id] = guild_data
        guild_data.entries[faq_entry.name] = faq_entry
        await self.dirty()

    async def remove_guild_faq(self, guild: Guild, faq_name: str) -> Optional[FaqEntry]:
        if guild_data := self.get_guild_data(guild):
            removed_entry = guild_data.entries.pop(faq_name, None)
            await self.dirty()
            return removed_entry
