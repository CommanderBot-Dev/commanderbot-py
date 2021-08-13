from dataclasses import dataclass

from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class ThrowError(AutomodConditionBase):
    error: str

    async def check(self, event: AutomodEvent) -> bool:
        raise Exception(self.error)


def create_condition(data: JsonObject) -> AutomodCondition:
    return ThrowError.from_data(data)
