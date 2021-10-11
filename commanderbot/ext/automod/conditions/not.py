from dataclasses import dataclass
from typing import Any, Dict, Optional

from commanderbot.ext.automod.condition import (
    Condition,
    ConditionBase,
    ConditionCollection,
)
from commanderbot.ext.automod.event import Event


@dataclass
class Not(ConditionBase):
    """
    Passes if any of the sub-conditions fail.

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
                return True
        return False


def create_condition(data: Any) -> Condition:
    return Not.from_data(data)
