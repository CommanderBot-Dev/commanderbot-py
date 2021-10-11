from dataclasses import dataclass
from typing import Any, Dict, Optional

from commanderbot.ext.automod.condition import (
    Condition,
    ConditionBase,
    ConditionCollection,
)
from commanderbot.ext.automod.event import Event


@dataclass
class AllOf(ConditionBase):
    """
    Check if all sub-conditions pass (logical AND).

    Note that this is effectively equivalent to `any_of` with a `count` set to the
    number of sub-conditions. The distinction exists for clarity and convenience.

    Attributes
    ----------
    conditions
        The sub-conditions to check.
    """

    conditions: ConditionCollection

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        conditions = ConditionCollection.from_data(data["conditions"])
        return dict(
            conditions=conditions,
        )

    async def check(self, event: Event) -> bool:
        for condition in self.conditions:
            if not await condition.check(event):
                return False
        return True


def create_condition(data: Any) -> Condition:
    return AllOf.from_data(data)
