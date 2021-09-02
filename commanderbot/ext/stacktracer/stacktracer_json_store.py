from dataclasses import dataclass
from typing import Optional

from discord import Guild

from commanderbot.ext.stacktracer.stacktracer_data import StacktracerData
from commanderbot.lib import CogStore, JsonFileDatabaseAdapter, LogOptions


# @implements StacktracerStore
@dataclass
class StacktracerJsonStore(CogStore):
    """
    Implementation of `StacktracerStore` that uses a simple JSON file to persist state.
    """

    db: JsonFileDatabaseAdapter[StacktracerData]

    # @implements StacktracerStore
    async def get_global_log_options(self) -> Optional[LogOptions]:
        cache = await self.db.get_cache()
        return await cache.get_global_log_options()

    # @implements StacktracerStore
    async def set_global_log_options(
        self, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        cache = await self.db.get_cache()
        old_value = await cache.set_global_log_options(log_options)
        await self.db.dirty()
        return old_value

    # @implements StacktracerStore
    async def get_guild_log_options(self, guild: Guild) -> Optional[LogOptions]:
        cache = await self.db.get_cache()
        return await cache.get_guild_log_options(guild)

    # @implements StacktracerStore
    async def set_guild_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        cache = await self.db.get_cache()
        old_value = await cache.set_guild_log_options(guild, log_options)
        await self.db.dirty()
        return old_value
