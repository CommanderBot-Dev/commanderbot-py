from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject
from commanderbot_ext.lib.integer_range import IntegerRange

ST = TypeVar("ST")


@dataclass
class MessageHasLinks(AutomodConditionBase):
    """
    Check if the message has links.

    Attributes
    ----------
    count
        The number of links to check for, if bounded.
    """

    # TODO Implement a configurable set of allowed domains? #enhance
    # TODO Implement configurable unicode normalization? #enhance

    count: Optional[IntegerRange] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        count = IntegerRange.from_field_optional(data, "count")
        return cls(
            description=data.get("description"),
            count=count,
        )

    async def check(self, event: AutomodEvent) -> bool:
        message = event.message
        if (message is None) or not message.content:
            return False
        content = str(message.content)
        count_http = content.count("http://")
        count_https = content.count("https://")
        count_links = count_http + count_https
        if self.count is not None:
            return self.count.includes(count_links)
        return count_links > 0


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageHasLinks.from_data(data)
