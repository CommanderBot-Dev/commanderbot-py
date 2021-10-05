from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, Iterable, Iterator, List, Optional, Type, TypeVar

from commanderbot.ext.automod.node.node import Node
from commanderbot.lib import FromData, ResponsiveException, ToData
from commanderbot.lib.utils import JsonPath, JsonPathOp, update_json_with_path

__all__ = (
    "NodeWithNameAlreadyExists",
    "NoNodeWithName",
    "NodeNotRegistered",
    "UnexpectedNodeType",
    "NodeCollection",
)


ST = TypeVar("ST", bound="NodeCollection")
NT = TypeVar("NT", bound=Node)
SNT = TypeVar("SNT", bound=Node)


class NodeWithNameAlreadyExists(ResponsiveException):
    def __init__(self, name: str):
        self.name: str = name
        super().__init__(f"A node with the name `{name}` already exists")


class NoNodeWithName(ResponsiveException):
    def __init__(self, name: str):
        self.name: str = name
        super().__init__(f"There is no node with the name `{name}`")


class NodeNotRegistered(ResponsiveException):
    def __init__(self, node: Node):
        self.node: Node = node
        super().__init__(f"Node `{node.name}` is not registered")


class UnexpectedNodeType(ResponsiveException):
    def __init__(self, node: Node):
        self.node: Node = node
        super().__init__(f"Unexpected node type `{type(node).__name__}`")


# @abstract
@dataclass(init=False)
class NodeCollection(FromData, ToData, Generic[NT]):
    """A collection of nodes with the same base type."""

    _nodes: List[NT]
    _nodes_by_name: Dict[str, NT]

    @classmethod
    @property
    @abstractmethod
    def node_type(cls) -> Type[NT]:
        ...

    @classmethod
    def build_node_from_data(cls: Type[ST], data: Any) -> NT:
        return cls.node_type.from_data(data)

    # @overrides FromData
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, list):
            nodes = [cls.build_node_from_data(node_data) for node_data in data]
            return cls(nodes)

    def __init__(self, nodes: Optional[Iterable[NT]] = None):
        self._nodes = []
        self._nodes_by_name = {}
        if nodes:
            for node in nodes:
                self.add(node)

    def __iter__(self) -> Iterator[NT]:
        return iter(self._nodes)

    # @overrides ToData
    def to_data(self) -> Any:
        return list(node.to_data() for node in self._nodes)

    def query(self, query: str) -> Iterable[NT]:
        # Yield any nodes whose name contains the case-insensitive query.
        query_lower = query.lower()
        for node in self:
            if query_lower in node.name.lower():
                yield node

    def get(self, name: str) -> Optional[NT]:
        return self._nodes_by_name.get(name)

    def require(self, name: str) -> NT:
        if node := self.get(name):
            return node
        raise NoNodeWithName(name)

    def require_with_type(self, name: str, node_type: Type[SNT]) -> SNT:
        node = self.require(name)
        if not isinstance(node, node_type):
            raise UnexpectedNodeType(node)
        return node

    def _add_to_cache(self, node: NT):
        self._nodes_by_name[node.name] = node

    def add(self, node: NT):
        if node.name in self._nodes_by_name:
            raise NodeWithNameAlreadyExists(node.name)
        self._nodes.append(node)
        self._add_to_cache(node)

    def add_from_data(self, data: Any) -> NT:
        node = self.build_node_from_data(data)
        self.add(node)
        return node

    def _remove_from_cache(self, node: NT):
        del self._nodes_by_name[node.name]

    def remove(self, node: NT):
        existing_node = self.require(node.name)
        if not (existing_node and (existing_node is node)):
            raise NodeNotRegistered(node)
        self._nodes.remove(node)
        self._remove_from_cache(node)

    def remove_by_name(self, name: str) -> NT:
        node = self.require(name)
        self.remove(node)
        return node

    def enable_by_name(self, name: str) -> NT:
        node = self.require(name)
        node.disabled = None
        return node

    def disable_by_name(self, name: str) -> NT:
        node = self.require(name)
        node.disabled = True
        return node

    def get_index(self, node: NT) -> int:
        for i, n in enumerate(self._nodes):
            if n is node:
                return i
        raise NodeNotRegistered(node)

    def replace(self, old_node: NT, new_node: NT):
        # Determine the index of the old node and replace it with the new one.
        index = self.get_index(old_node)
        self._nodes[index] = new_node
        self._remove_from_cache(old_node)
        self._add_to_cache(new_node)

    def modify(self, name: str, path: JsonPath, op: JsonPathOp, data: Any) -> NT:
        # Start with the serialized form of the original node.
        old_node = self.require(name)
        new_data = old_node.to_data()

        # Update the new node data using the given changes.
        new_data = update_json_with_path(new_data, path, op, data)

        # Create a new node out of the modified data.
        new_node = self.build_node_from_data(new_data)

        # Replace the old node with the new one.
        self.replace(old_node, new_node)

        # Return the new node.
        return new_node
