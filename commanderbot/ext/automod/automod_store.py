from typing import Any, AsyncIterable, Optional, Protocol, Type, TypeVar

from discord import Guild

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.node import Node
from commanderbot.ext.automod.rule import Rule
from commanderbot.lib import LogOptions, RoleSet
from commanderbot.lib.utils import JsonPath, JsonPathOp

NT = TypeVar("NT", bound=Node)


class AutomodStore(Protocol):
    """
    Abstracts the data storage and persistence of the automod cog.
    """

    # @@ OPTIONS

    async def get_default_log_options(self, guild: Guild) -> Optional[LogOptions]:
        ...

    async def set_default_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        ...

    async def get_permitted_roles(self, guild: Guild) -> Optional[RoleSet]:
        ...

    async def set_permitted_roles(
        self, guild: Guild, permitted_roles: Optional[RoleSet]
    ) -> Optional[RoleSet]:
        ...

    # @@ NODES

    def all_nodes(self, guild: Guild, node_type: Type[NT]) -> AsyncIterable[NT]:
        ...

    def query_nodes(
        self, guild: Guild, node_type: Type[NT], query: str
    ) -> AsyncIterable[NT]:
        ...

    async def get_node(
        self, guild: Guild, node_type: Type[NT], name: str
    ) -> Optional[NT]:
        ...

    async def require_node(self, guild: Guild, node_type: Type[NT], name: str) -> NT:
        ...

    async def require_node_with_type(
        self, guild: Guild, node_type: Type[NT], name: str
    ) -> NT:
        ...

    async def add_node(self, guild: Guild, node_type: Type[NT], data: Any) -> NT:
        ...

    async def remove_node(self, guild: Guild, node_type: Type[NT], name: str) -> NT:
        ...

    async def enable_node(self, guild: Guild, node_type: Type[NT], name: str) -> NT:
        ...

    async def disable_node(self, guild: Guild, node_type: Type[NT], name: str) -> NT:
        ...

    async def modify_node(
        self,
        guild: Guild,
        node_type: Type[NT],
        name: str,
        path: JsonPath,
        op: JsonPathOp,
        data: Any,
    ) -> NT:
        ...

    # @@ RULES

    def rules_for_event(self, guild: Guild, event: AutomodEvent) -> AsyncIterable[Rule]:
        ...

    async def increment_rule_hits(self, guild: Guild, name: str) -> Rule:
        ...
