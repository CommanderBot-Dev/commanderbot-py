from typing import Any, Optional, Protocol, Type, TypeVar

__all__ = ("Node",)


ST = TypeVar("ST")


class Node(Protocol):
    """
    Base interface for automod nodes.

    Nodes are generally anything that can be saved to data, loaded from data, and
    referenced by name.
    """

    name: str
    description: Optional[str]
    disabled: Optional[bool]

    @classmethod
    def from_data(cls: Type[ST], data: Any) -> ST:
        """Create a node from raw data."""

    def to_data(self) -> Any:
        """Turn the node into raw data."""

    def build_title(self) -> str:
        """Return a human-readable title for the node."""
