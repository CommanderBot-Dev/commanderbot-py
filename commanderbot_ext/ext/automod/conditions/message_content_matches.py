import unicodedata
from dataclasses import dataclass
from typing import Optional, Type, TypeVar

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
    Check if message content matches a regular expression.

    Attributes
    ----------
    pattern
        The regular expression to match against.
    use_search
        Whether to search the entire string instead of using an anchored match.
    use_normalization
        Whether to use unicode normalization or process the string as-is.
    normalization_form
        If enabled, the type of normalization to apply. Defaults to NFKD.
    """

    pattern: PatternWrapper

    use_search: Optional[bool] = None
    use_normalization: Optional[bool] = None
    normalization_form: Optional[str] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        pattern = PatternWrapper.from_field(data, "pattern")
        return cls(
            description=data.get("description"),
            pattern=pattern,
            use_search=data.get("search"),
            use_normalization=data.get("use_normalization"),
            normalization_form=data.get("normalization_form"),
        )

    async def check(self, event: AutomodEvent) -> bool:
        message = event.message
        # Short-circuit if there's no message or the message is empty.
        if not (message and message.content):
            return False
        content = message.content
        if self.use_normalization:
            normalization_form = self.normalization_form or DEFAULT_NORMALIZATION_FORM
            content = unicodedata.normalize(normalization_form, content)
        if self.use_search:
            match = self.pattern.search(content)
            return bool(match)
        match = self.pattern.match(content)
        return bool(match)


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageContentMatches.from_data(data)
