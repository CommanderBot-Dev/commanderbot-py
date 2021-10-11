import typing
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Optional, Type, TypeVar, cast

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.node.node import Node
from commanderbot.lib import FromData, ToData

__all__ = ("NodeRef",)


ST = TypeVar("ST")
NT = TypeVar("NT", bound=Node)


# @abstract
@dataclass
class NodeRef(FromData, ToData, Generic[NT]):
    """A reference to a node, by name."""

    name: str

    @classmethod
    @property
    @abstractmethod
    def node_type(cls) -> Type[NT]:
        """Return the concrete node type used to construct instances."""

    # @overrides FromData
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, str):
            return cls(name=data)

    # @overrides ToData
    def to_data(self) -> Any:
        return self.name

    async def resolve(self, event: AutomodEvent) -> NT:
        node = await event.state.store.require_node_with_type(
            event.state.guild, self.node_type, self.name
        )
        return node
