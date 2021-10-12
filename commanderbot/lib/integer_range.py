from dataclasses import dataclass
from typing import Any, Optional, Type, TypeVar

from commanderbot.lib.data import FromData, ToData

__all__ = ("IntegerRange",)


ST = TypeVar("ST")


@dataclass
class IntegerRange(FromData, ToData):
    """
    An integer range with optional upper and lower bounds.

    Attributes
    ----------
    min
        The lower bound of the range.
    max
        The upper bound of the range.
    """

    min: Optional[int] = None
    max: Optional[int] = None

    # @overrides FromData
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, int):
            return cls(min=data, max=data)
        elif isinstance(data, list):
            args = dict(
                min=data[0],
                max=data[1],
            )
            args = {k: v for k, v in args.items() if v is not ...}
            return cls(**args)
        elif isinstance(data, dict):
            return cls(**data)

    def includes(self, value: int) -> bool:
        if (self.min is not None) and (value < self.min):
            return False
        if (self.max is not None) and (value > self.max):
            return False
        return True

    def excludes(self, count: int) -> bool:
        return not self.includes(count)
