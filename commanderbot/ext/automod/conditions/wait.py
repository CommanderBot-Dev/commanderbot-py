import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, Optional

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.condition import Condition, ConditionBase
from commanderbot.lib.utils import timedelta_from_field_optional


@dataclass
class Wait(ConditionBase):
    """
    Wait a certain amount of time before continuing.

    Attributes
    ----------
    delay
        How long to wait for.
    """

    delay: timedelta

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        delay = timedelta_from_field_optional(data, "delay")
        return dict(delay=delay)

    async def check(self, event: AutomodEvent) -> bool:
        await asyncio.sleep(self.delay.total_seconds())
        return True


def create_condition(data: Any) -> Condition:
    return Wait.from_data(data)
