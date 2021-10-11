import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, TypeVar

from commanderbot.lib import FromData, ToData

__all__ = ("NodeBase",)


ST = TypeVar("ST", bound="NodeBase")


# @implements Node
@dataclass
class NodeBase(FromData, ToData):
    """
    Base implementation for automod nodes.

    See `Node` for a description of what nodes are.

    There isn't much here, other than base logic for the de/serialization methods.

    Attributes
    ----------
    name
        The name of the node. Can be any arbitrary string, but snake_case tends to be
        easier to type into chat.
    description
        A human-readable description of the node.
    disabled
        Whether the node is currently disabled.
    """

    # @implements Node
    name: str

    # @implements Node
    description: Optional[str]

    # @implements Node
    disabled: Optional[bool]

    # @overrides FromData
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, dict):
            processed_data = cls.build_processed_data(data)
            obj = cls(**processed_data)
            return obj

    @classmethod
    def new_node_name(cls) -> str:
        """Create a new, unique node name."""
        return str(uuid.uuid4())

    @classmethod
    def build_base_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-fill required dataclass fields that aren't necessarily required in data.

        Currently this includes the `name`, `description`, and `disabled` fields, which
        are required dataclass fields not necessarily required in data.
        """
        name = data.get("name")
        if not name:
            name = cls.new_node_name()
        base_data: Dict[str, Any] = {
            "name": name,
            "description": None,
            "disabled": None,
        }
        base_data.update(data)
        return base_data

    @classmethod
    def build_processed_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-fill required dataclass fields and include extracted fields."""
        # Start with the base data.
        processed_data = cls.build_base_data(data)

        # If complex fields are present, include them.
        if complex_fields := cls.build_complex_fields(data):
            processed_data.update(complex_fields)

        # Return the final, processed data.
        return processed_data

    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Return nested objects that must themselves be constructed from raw data."""

    # @implements Node
    def build_title(self) -> str:
        parts = [f"{self.name}:"]
        if self.description:
            parts.append(self.description)
        return " ".join(parts)
