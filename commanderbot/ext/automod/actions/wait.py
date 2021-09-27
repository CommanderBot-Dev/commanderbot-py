import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Type, TypeVar

from commanderbot.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject
from commanderbot.lib.utils import timedelta_from_field_optional

ST = TypeVar("ST")


@dataclass
class Wait(AutomodActionBase):
    """
    Wait a certain amount of time before continuing.

    Attributes
    ----------
    delay
        How long to wait for.
    """

    delay: timedelta

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        delay = timedelta_from_field_optional(data, "delay")
        return cls(
            description=data.get("description"),
            delay=delay,
        )

    async def apply(self, event: AutomodEvent):
        await asyncio.sleep(self.delay.total_seconds())


def create_action(data: JsonObject) -> AutomodAction:
    return Wait.from_data(data)
