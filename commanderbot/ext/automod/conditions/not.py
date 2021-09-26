from dataclasses import dataclass
from typing import Tuple, Type, TypeVar

from commanderbot.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
    deserialize_conditions,
)
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class Not(AutomodConditionBase):
    """
    Passes if any of the sub-conditions fail.

    Attributes
    ----------
    conditions
        The sub-conditions to check.
    """

    conditions: Tuple[AutomodCondition]

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        raw_conditions = data["conditions"]
        conditions = deserialize_conditions(raw_conditions)
        return cls(
            description=data.get("description"),
            conditions=conditions,
        )

    async def check(self, event: AutomodEvent) -> bool:
        for condition in self.conditions:
            if not await condition.check(event):
                return True
        return False


def create_condition(data: JsonObject) -> AutomodCondition:
    return Not.from_data(data)
