import unicodedata
from dataclasses import dataclass
from typing import Optional, Tuple, Type, TypeVar

from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject, PatternWrapper

ST = TypeVar("ST")


DEFAULT_NORMALIZATION_FORM = "NFKD"


@dataclass
class MessageContentMatches(AutomodConditionBase):
    """
    Check if message content matches a number of regular expressions.

    Attributes
    ----------
    matches
        The patterns (regular expressions) to match.
    count
        The number of unique patterns to match. For example: a value of 1 requires any
        of the patterns to be matched, whereas a value of requires at least 2 to be
        matched. If unspecified, all patterns must be matched.
    use_search
        Whether to search the entire string instead of using an anchored match.
    use_normalization
        Whether to use unicode normalization or process the string as-is.
    normalization_form
        If enabled, the type of normalization to apply. Defaults to NFKD.
    """

    matches: Tuple[PatternWrapper]
    count: Optional[int] = None
    use_search: Optional[bool] = None
    use_normalization: Optional[bool] = None
    normalization_form: Optional[str] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        raw_matches = data["matches"]
        if isinstance(raw_matches, (str, dict)):
            matches = [PatternWrapper.from_data(raw_matches)]
        else:
            matches = [PatternWrapper.from_data(item) for item in raw_matches]
        return cls(
            description=data.get("description"),
            matches=matches,
            count=data.get("count"),
            use_search=data.get("use_search"),
            use_normalization=data.get("use_normalization"),
            normalization_form=data.get("normalization_form"),
        )

    def is_match(self, pattern: PatternWrapper, content: str) -> bool:
        if self.use_search:
            match = pattern.search(content)
            return bool(match)
        match = pattern.match(content)
        return bool(match)

    async def check(self, event: AutomodEvent) -> bool:
        message = event.message
        # Short-circuit if there's no message or the message is empty.
        if not (message and message.content):
            return False
        # Otherwise, check for a sufficient number of matches.
        content = message.content
        if self.use_normalization:
            normalization_form = self.normalization_form or DEFAULT_NORMALIZATION_FORM
            content = unicodedata.normalize(normalization_form, content)
        remainder = self.count or len(self.matches)
        for pattern in self.matches:
            if self.is_match(pattern, content):
                remainder -= 1
                if remainder <= 0:
                    return True
        return False


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageContentMatches.from_data(data)
