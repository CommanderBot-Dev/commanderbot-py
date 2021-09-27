import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Type, TypeVar

from commanderbot.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject
from commanderbot.lib.utils import timedelta_from_field_optional

ST = TypeVar("ST")


@dataclass
class Wait(AutomodConditionBase):
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

    async def check(self, event: AutomodEvent) -> bool:
        await asyncio.sleep(self.delay.total_seconds())
        return True


def create_condition(data: JsonObject) -> AutomodCondition:
    return Wait.from_data(data)
