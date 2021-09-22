import re
from dataclasses import dataclass
from typing import Any, AnyStr, Match, Optional, Type, TypeVar

from commanderbot.lib.data import FromData, ToData

__all__ = ("PatternWrapper",)


ST = TypeVar("ST")


@dataclass
class PatternWrapper(FromData, ToData):
    """Wraps `re.Pattern` to simplify de/serialization."""

    pattern: re.Pattern

    # TODO Other regex flags? #enhance
    ignore_case: Optional[bool] = None

    # @overrides FromData
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, str):
            pattern = re.compile(data)
            return cls(pattern)
        elif isinstance(data, dict):
            raw_pattern = data["pattern"]
            ignore_case = data.get("ignore_case")
            flags = 0
            if ignore_case:
                flags |= re.IGNORECASE
            pattern = re.compile(raw_pattern, flags=flags)
            return cls(
                pattern=pattern,
                ignore_case=ignore_case,
            )

    # @overrides ToData
    def to_data(self) -> Any:
        if self.ignore_case:
            return dict(
                pattern=self.pattern.pattern,
                ignore_case=self.ignore_case,
            )
        return self.pattern.pattern

    def search(self, string: AnyStr) -> Optional[Match[AnyStr]]:
        return self.pattern.search(string)

    def match(self, string: AnyStr) -> Optional[Match[AnyStr]]:
        return self.pattern.match(string)
