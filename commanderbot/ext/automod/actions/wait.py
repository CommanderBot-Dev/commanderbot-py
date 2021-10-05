import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, Optional

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib.utils import timedelta_from_field_optional


@dataclass
class Wait(ActionBase):
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

    async def apply(self, event: AutomodEvent):
        await asyncio.sleep(self.delay.total_seconds())


def create_action(data: Any) -> Action:
    return Wait.from_data(data)
