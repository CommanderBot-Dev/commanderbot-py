from dataclasses import dataclass
from typing import Optional

from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class MessageContentContains(AutomodConditionBase):
    """
    Check if message content contains a string.

    Attributes
    ----------
    content
        The string to check for.
    ignore_case
        Whether to ignore upper vs lower case.
    """

    content: str
    ignore_case: Optional[bool] = None

    async def check(self, event: AutomodEvent) -> bool:
        message = event.message
        # Short-circuit if there's no message or the message is empty.
        if not (message and message.content):
            return False
        lhs, rhs = str(message.content), self.content
        # Short-circuit if LHS is too short to contain RHS.
        if len(lhs) < len(rhs):
            return False
        if self.ignore_case:
            lhs, rhs = lhs.lower(), rhs.lower()
        return rhs in lhs


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageContentContains.from_data(data)
