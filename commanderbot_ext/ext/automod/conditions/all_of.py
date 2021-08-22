from dataclasses import dataclass
from typing import Tuple, Type, TypeVar

from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
    deserialize_conditions,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class AllOf(AutomodConditionBase):
    """
    Check if all sub-conditions pass (logical AND).

    Note that this is effectively equivalent to `any_of` with a `count` set to the
    number of sub-conditions. The distinction exists for clarity and convenience.

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
                return False
        return True


def create_condition(data: JsonObject) -> AutomodCondition:
    return AllOf.from_data(data)
