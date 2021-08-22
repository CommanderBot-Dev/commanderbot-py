from dataclasses import dataclass
from typing import Optional, Tuple, Type, TypeVar

from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class MessageContentContains(AutomodConditionBase):
    """
    Check if message content contains a number of strings.

    Attributes
    ----------
    contains
        The strings to find.
    count
        The number of unique substrings to find. For example: a value of 1 requires any
        of the substrings to be found, whereas a value of 2 requires at least 2 to be
        found. If unspecified, all substrings must be found.
    ignore_case
        Whether to ignore upper vs lower case.
    """

    contains: Tuple[str]
    count: Optional[int] = None
    ignore_case: Optional[bool] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        raw_contains = data["contains"]
        if isinstance(raw_contains, str):
            contains = [raw_contains]
        else:
            contains = [str(item) for item in raw_contains]
        ignore_case = data.get("ignore_case")
        if ignore_case:
            contains = [item.lower() for item in contains]
        return cls(
            description=data.get("description"),
            contains=contains,
            count=data.get("count"),
            ignore_case=ignore_case,
        )

    async def check(self, event: AutomodEvent) -> bool:
        message = event.message
        # Short-circuit if there's no message or the message is empty.
        if not (message and message.content):
            return False
        # Otherwise, check for a sufficient number of matches.
        content = str(message.content)
        if self.ignore_case:
            content = content.lower()
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


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageContentContains.from_data(data)
