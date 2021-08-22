from dataclasses import dataclass
from typing import Optional, Tuple, Type, TypeVar

from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
    deserialize_conditions,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class AnyOf(AutomodConditionBase):
    """
    Check if a number of sub-conditions pass (logical OR).

    Attributes
    ----------
    conditions
        The sub-conditions to check.
    count
        The number of sub-conditions that must pass. If unspecified, only a single
        sub-condition is required to pass.
    """

    conditions: Tuple[AutomodCondition]
    count: Optional[int] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        raw_conditions = data["conditions"]
        conditions = deserialize_conditions(raw_conditions)
        return cls(
            description=data.get("description"),
            conditions=conditions,
            count=data.get("count"),
        )

    async def check(self, event: AutomodEvent) -> bool:
        remainder = self.count or 1
        for condition in self.conditions:
            if await condition.check(event):
                remainder -= 1
                if remainder <= 0:
                    return True
        return False


def create_condition(data: JsonObject) -> AutomodCondition:
    return AnyOf.from_data(data)
