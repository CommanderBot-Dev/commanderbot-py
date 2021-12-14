from dataclasses import dataclass
from typing import Any, Dict, Optional

from commanderbot.ext.automod.condition import Condition, ConditionBase
from commanderbot.ext.automod.event import Event
from commanderbot.lib import IntegerRange


@dataclass
class MessageHasAttachments(ConditionBase):
    """
    Check if the message has attachments.

    Attributes
    ----------
    count
        The number of attachments to check for, if bounded.
    """

    count: Optional[IntegerRange] = None

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        count = IntegerRange.from_field_optional(data, "count")
        return dict(
            count=count,
        )

    async def check(self, event: Event) -> bool:
        message = event.message
        if message is None:
            return False
        count_attachments = len(message.attachments or [])
        if self.count is not None:
            return self.count.includes(count_attachments)
        return count_attachments > 0


def create_condition(data: Any) -> Condition:
    return MessageHasAttachments.from_data(data)
