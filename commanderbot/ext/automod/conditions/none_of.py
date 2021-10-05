from dataclasses import dataclass
from typing import Any, Dict, Optional

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.condition import (
    Condition,
    ConditionBase,
    ConditionCollection,
)


@dataclass
class NoneOf(ConditionBase):
    """
    Passes if and only if none of the sub-conditions pass.

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

    async def check(self, event: AutomodEvent) -> bool:
        for condition in self.conditions:
            if await condition.check(event):
                return False
        return True


def create_condition(data: Any) -> Condition:
    return NoneOf.from_data(data)
