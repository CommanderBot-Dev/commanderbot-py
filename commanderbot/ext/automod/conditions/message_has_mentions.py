from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from commanderbot.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject
from commanderbot.lib.integer_range import IntegerRange

ST = TypeVar("ST")


@dataclass
class MessageHasMentions(AutomodConditionBase):
    """
    Check if the message has mentions.

    Attributes
    ----------
    count
        The number of mentions to check for, if bounded.
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
        if message is None:
            return False
        count_user_mentions = len(message.mentions)
        count_role_mentions = len(message.role_mentions)
        count_mentions = count_user_mentions + count_role_mentions
        if self.count is not None:
            return self.count.includes(count_mentions)
        return count_mentions > 0


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageHasMentions.from_data(data)
