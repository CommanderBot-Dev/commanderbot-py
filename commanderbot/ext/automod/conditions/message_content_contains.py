import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.condition import Condition, ConditionBase
from commanderbot.lib import JsonObject

DEFAULT_NORMALIZATION_FORM = "NFKD"


@dataclass
class MessageContentContains(ConditionBase):
    """
    Check if message content contains a number of substrings.

    Attributes
    ----------
    contains
        The substrings to find. Unless `count` is specified, all substrings must be
        found in order to pass.
    count
        The number of unique substrings to find. For example: a value of 1 requires any
        of the substrings to be found, whereas a value of 2 requires at least 2 to be
        found. If unspecified, all substrings must be found.
    ignore_case
        Whether to ignore upper vs lower case.
    use_normalization
        Whether to use unicode normalization or process the string as-is.
    normalization_form
        If enabled, the type of normalization to apply. Defaults to NFKD.
    """

    contains: Tuple[str]
    count: Optional[int] = None
    ignore_case: Optional[bool] = None
    use_normalization: Optional[bool] = None
    normalization_form: Optional[str] = None

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raw_contains = data["contains"]
        if isinstance(raw_contains, str):
            contains = [raw_contains]
        else:
            contains = [str(item) for item in raw_contains]

        if data.get("ignore_case"):
            contains = [item.lower() for item in contains]

        return dict(
            contains=contains,
        )

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
        # Convert the message content to lower-case, if we're ignoring case.
        if self.ignore_case:
            content = content.lower()
        # Check for a sufficient number of substrings.
        remainder = self.count or len(self.contains)
        for substring in self.contains:
            # If the substring is found, adjust the counter.
            if substring in content:
                remainder -= 1
                # If the threshold is hit, return immediately instead of looking for
                # further redundant matches.
                if remainder <= 0:
                    return True
        # If we get this far, it means we exhausted all of the potential matches without
        # reaching the required number of matches.
        return False


def create_condition(data: JsonObject) -> Condition:
    return MessageContentContains.from_data(data)
