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
class MessageHasEmbeds(AutomodConditionBase):
    """
    Check if the message has embeds.

    Attributes
    ----------
    count
        The number of embeds to check for, if bounded.
    """

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
        count_embeds = len(message.embeds or [])
        if self.count is not None:
            return self.count.includes(count_embeds)
        return count_embeds > 0


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageHasEmbeds.from_data(data)
