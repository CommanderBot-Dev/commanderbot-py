from dataclasses import dataclass
from typing import Any, Dict, Optional

from commanderbot.ext.automod.condition import Condition, ConditionBase
from commanderbot.ext.automod.event import Event
from commanderbot.lib import IntegerRange


@dataclass
class MessageHasLinks(ConditionBase):
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

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        count = IntegerRange.from_field_optional(data, "count")
        return dict(
            count=count,
        )

    async def check(self, event: Event) -> bool:
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


def create_condition(data: Any) -> Condition:
    return MessageHasLinks.from_data(data)
