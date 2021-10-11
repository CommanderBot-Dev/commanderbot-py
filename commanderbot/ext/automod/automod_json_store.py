from dataclasses import dataclass
from typing import Any, AsyncIterable, Optional, Type, TypeVar

from discord import Guild

from commanderbot.ext.automod.automod_data import AutomodData
from commanderbot.ext.automod.bucket import Bucket
from commanderbot.ext.automod.event import Event
from commanderbot.ext.automod.node import Node
from commanderbot.ext.automod.rule import Rule
from commanderbot.lib import CogStore, JsonFileDatabaseAdapter, LogOptions, RoleSet
from commanderbot.lib.utils import JsonPath, JsonPathOp

BT = TypeVar("BT", bound=Bucket)
NT = TypeVar("NT", bound=Node)


# @implements AutomodStore
@dataclass
class AutomodJsonStore(CogStore):
    """
    Implementation of `AutomodStore` that uses a simple JSON file to persist state.
    """

    db: JsonFileDatabaseAdapter[AutomodData]

    # @@ OPTIONS

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

    # @@ NODES

    # @implements AutomodStore
    async def all_nodes(self, guild: Guild, node_type: Type[NT]) -> AsyncIterable[NT]:
        cache = await self.db.get_cache()
        async for node in cache.all_nodes(guild, node_type):
            yield node

    # @implements AutomodStore
    async def query_nodes(
        self, guild: Guild, node_type: Type[NT], query: str
    ) -> AsyncIterable[NT]:
        cache = await self.db.get_cache()
        async for node in cache.query_nodes(guild, node_type, query):
            yield node

    # @implements AutomodStore
    async def get_node(
        self, guild: Guild, node_type: Type[NT], name: str
    ) -> Optional[NT]:
        cache = await self.db.get_cache()
        return await cache.get_node(guild, node_type, name)

    # @implements AutomodStore
    async def require_node(self, guild: Guild, node_type: Type[NT], name: str) -> NT:
        cache = await self.db.get_cache()
        return await cache.require_node(guild, node_type, name)

    # @implements AutomodStore
    async def require_node_with_type(
        self, guild: Guild, node_type: Type[NT], name: str
    ) -> NT:
        cache = await self.db.get_cache()
        return await cache.require_node_with_type(guild, node_type, name)

    # @implements AutomodStore
    async def add_node(self, guild: Guild, node_type: Type[NT], data: Any) -> NT:
        cache = await self.db.get_cache()
        added_node = await cache.add_node(guild, node_type, data)
        await self.db.dirty()
        return added_node

    # @implements AutomodStore
    async def remove_node(self, guild: Guild, node_type: Type[NT], name: str) -> NT:
        cache = await self.db.get_cache()
        removed_node = await cache.remove_node(guild, node_type, name)
        await self.db.dirty()
        return removed_node

    # @implements AutomodStore
    async def enable_node(self, guild: Guild, node_type: Type[NT], name: str) -> NT:
        cache = await self.db.get_cache()
        modified_node = await cache.enable_node(guild, node_type, name)
        await self.db.dirty()
        return modified_node

    # @implements AutomodStore
    async def disable_node(self, guild: Guild, node_type: Type[NT], name: str) -> NT:
        cache = await self.db.get_cache()
        modified_node = await cache.disable_node(guild, node_type, name)
        await self.db.dirty()
        return modified_node

    # @implements AutomodStore
    async def modify_node(
        self,
        guild: Guild,
        node_type: Type[NT],
        name: str,
        path: JsonPath,
        op: JsonPathOp,
        data: Any,
    ) -> NT:
        cache = await self.db.get_cache()
        modified_node = await cache.modify_node(guild, node_type, name, path, op, data)
        await self.db.dirty()
        return modified_node

    # @@ RULES

    # @implements AutomodStore
    async def rules_for_event(self, guild: Guild, event: Event) -> AsyncIterable[Rule]:
        cache = await self.db.get_cache()
        async for rule in cache.rules_for_event(guild, event):
            yield rule

    # @implements AutomodStore
    async def increment_rule_hits(self, guild: Guild, name: str) -> Rule:
        cache = await self.db.get_cache()
        modified_rule = await cache.increment_rule_hits(guild, name)
        await self.db.dirty()
        return modified_rule
