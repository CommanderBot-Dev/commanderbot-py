from abc import ABC, abstractmethod
from typing import Any

__all__ = ("JsonSerializable",)


class JsonSerializable(ABC):
    @abstractmethod
    def to_json(self) -> Any:
        """Turn the object into JSON-serializable data."""
