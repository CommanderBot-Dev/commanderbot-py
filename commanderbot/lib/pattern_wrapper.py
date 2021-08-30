import re
from dataclasses import dataclass
from typing import Any, AnyStr, Match, Optional

from commanderbot_ext.lib.from_data_mixin import FromDataMixin
from commanderbot_ext.lib.json_serializable import JsonSerializable

__all__ = ("PatternWrapper",)


@dataclass
class PatternWrapper(JsonSerializable, FromDataMixin):
    """Wraps `re.Pattern` to simplify de/serialization."""

    pattern: re.Pattern

    # TODO Other regex flags? #enhance
    ignore_case: Optional[bool] = None

    @classmethod
    def try_from_str(cls, data: str):
        pattern = re.compile(data)
        return cls(pattern)

    @classmethod
    def try_from_dict(cls, data: dict):
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

    @classmethod
    def try_from_data(cls, data):
        if isinstance(data, str):
            return cls.try_from_str(data)
        elif isinstance(data, dict):
            return cls.try_from_dict(data)

    # @implements JsonSerializable
    def to_json(self) -> Any:
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
