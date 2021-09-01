from dataclasses import dataclass
from typing import AsyncIterable, Optional

from discord import Guild

from commanderbot.ext.automod.automod_data import AutomodData
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.automod_store import AutomodRule
from commanderbot.lib import (
    CogStore,
    JsonFileDatabaseAdapter,
    JsonObject,
    LogOptions,
    RoleSet,
)


# @implements AutomodStore
@dataclass
class AutomodJsonStore(CogStore):
    """
    Implementation of `AutomodStore` that uses a simple JSON file to persist state.
    """

    db: JsonFileDatabaseAdapter[AutomodData]

    # @implements AutomodStore
    async def get_default_log_options(self, guild: Guild) -> Optional[LogOptions]:
        cache = await self.db.get_cache()
        return await cache.get_default_log_options(guild)

    # @implements AutomodStore
    async def set_default_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        cache = await self.db.get_cache()
        old_value = await cache.set_default_log_options(guild, log_options)
        await self.db.dirty()
        return old_value

    # @implements AutomodStore
    async def get_permitted_roles(self, guild: Guild) -> Optional[RoleSet]:
        cache = await self.db.get_cache()
        return await cache.get_permitted_roles(guild)

    # @implements AutomodStore
    async def set_permitted_roles(
        self, guild: Guild, permitted_roles: Optional[RoleSet]
    ) -> Optional[RoleSet]:
        cache = await self.db.get_cache()
        old_value = await cache.set_permitted_roles(guild, permitted_roles)
        await self.db.dirty()
        return old_value

    # @implements AutomodStore
    async def all_rules(self, guild: Guild) -> AsyncIterable[AutomodRule]:
        cache = await self.db.get_cache()
        async for rule in cache.all_rules(guild):
            yield rule

    # @implements AutomodStore
    async def rules_for_event(
        self, guild: Guild, event: AutomodEvent
    ) -> AsyncIterable[AutomodRule]:
        cache = await self.db.get_cache()
        async for rule in cache.rules_for_event(guild, event):
            yield rule

    # @implements AutomodStore
    async def query_rules(self, guild: Guild, query: str) -> AsyncIterable[AutomodRule]:
        cache = await self.db.get_cache()
        async for rule in cache.query_rules(guild, query):
            yield rule

    # @implements AutomodStore
    async def get_rule(self, guild: Guild, name: str) -> Optional[AutomodRule]:
        cache = await self.db.get_cache()
        return await cache.get_rule(guild, name)

    # @implements AutomodStore
    async def require_rule(self, guild: Guild, name: str) -> AutomodRule:
        cache = await self.db.get_cache()
        return await cache.require_rule(guild, name)

    # @implements AutomodStore
    async def add_rule(self, guild: Guild, data: JsonObject) -> AutomodRule:
        cache = await self.db.get_cache()
        added_rule = await cache.add_rule(guild, data)
        await self.db.dirty()
        return added_rule

    # @implements AutomodStore
    async def remove_rule(self, guild: Guild, name: str) -> AutomodRule:
        cache = await self.db.get_cache()
        removed_rule = await cache.remove_rule(guild, name)
        await self.db.dirty()
        return removed_rule

    # @implements AutomodStore
    async def modify_rule(
        self, guild: Guild, name: str, data: JsonObject
    ) -> AutomodRule:
        cache = await self.db.get_cache()
        modified_rule = await cache.modify_rule(guild, name, data)
        await self.db.dirty()
        return modified_rule

    # @implements AutomodStore
    async def enable_rule(self, guild: Guild, name: str) -> AutomodRule:
        cache = await self.db.get_cache()
        modified_rule = await cache.enable_rule(guild, name)
        await self.db.dirty()
        return modified_rule

    # @implements AutomodStore
    async def disable_rule(self, guild: Guild, name: str) -> AutomodRule:
        cache = await self.db.get_cache()
        modified_rule = await cache.disable_rule(guild, name)
        await self.db.dirty()
        return modified_rule

    # @implements AutomodStore
    async def increment_rule_hits(self, guild: Guild, name: str) -> AutomodRule:
        cache = await self.db.get_cache()
        modified_rule = await cache.increment_rule_hits(guild, name)
        await self.db.dirty()
        return modified_rule
