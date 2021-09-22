import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.condition import Condition, ConditionBase
from commanderbot.lib import JsonObject, PatternWrapper

DEFAULT_NORMALIZATION_FORM = "NFKD"


@dataclass
class MessageContentMatches(ConditionBase):
    """
    Check if message content matches a number of regular expressions.

    Attributes
    ----------
    matches
        The patterns (regular expressions) to match. Unless `count` is specified, all
        patterns must be matched in order to pass.
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

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raw_matches = data["matches"]
        if isinstance(raw_matches, (str, dict)):
            matches = [PatternWrapper.from_data(raw_matches)]
        else:
            assert isinstance(raw_matches, list)
            matches = [PatternWrapper.from_data(item) for item in raw_matches]

        return dict(
            matches=matches,
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
        # Grab the message content.
        content = str(message.content)
        # Normalize the message content, if enabled.
        if self.use_normalization:
            normalization_form = self.normalization_form or DEFAULT_NORMALIZATION_FORM
            content = unicodedata.normalize(normalization_form, content)
        # Check for a sufficient number of matches.
        remainder = self.count or len(self.matches)
        for pattern in self.matches:
            # If there's a match, adjust the counter and check if we're done.
            if self.is_match(pattern, content):
                remainder -= 1
                if remainder <= 0:
                    return True
        # If we got this far, there weren't enough matches.
        return False


def create_condition(data: JsonObject) -> Condition:
    return MessageContentMatches.from_data(data)
