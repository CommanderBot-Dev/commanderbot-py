from dataclasses import dataclass
from typing import Any, Dict, Optional

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.condition import (
    Condition,
    ConditionBase,
    ConditionCollection,
)
from commanderbot.lib import JsonObject


@dataclass
class AnyOf(ConditionBase):
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

    conditions: ConditionCollection
    count: Optional[int] = None

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        conditions = ConditionCollection.from_data(data["conditions"])
        return dict(
            conditions=conditions,
        )

    async def check(self, event: AutomodEvent) -> bool:
        remainder = self.count or 1
        for condition in self.conditions:
            if await condition.check(event):
                remainder -= 1
                if remainder <= 0:
                    return True
        return False


def create_condition(data: JsonObject) -> Condition:
    return AnyOf.from_data(data)
