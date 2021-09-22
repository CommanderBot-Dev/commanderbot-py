import typing
from dataclasses import dataclass
from typing import Any, Generic, Optional, Type, TypeVar, cast

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.node.node import Node
from commanderbot.lib import FromData, ToData

__all__ = ("NodeRef",)


ST = TypeVar("ST")
NT = TypeVar("NT", bound=Node)


@dataclass
class NodeRef(FromData, ToData, Generic[NT]):
    """A reference to a node, by name."""

    name: str

    # @overrides FromData
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, str):
            return cls(name=data)

    # @overrides ToData
    def to_data(self) -> Any:
        return self.name

    @property
    def node_type(self) -> Type[NT]:
        # IMPL
        t_args = typing.get_args(self)
        t_origin = typing.get_origin(self)
        t_hints = typing.get_type_hints(self)
        node_type = t_args[0]
        assert issubclass(node_type, Node)
        return cast(Type[NT], node_type)

    async def resolve(self, event: AutomodEvent) -> NT:
        node = await event.state.store.require_node_with_type(
            event.state.guild, self.node_type, self.name
        )
        return node
