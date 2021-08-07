from abc import ABC, abstractmethod
from typing import Any


class JsonSerializable(ABC):
    @abstractmethod
    def to_json(self) -> Any:
        """Turn the object into JSON-serializable data."""
