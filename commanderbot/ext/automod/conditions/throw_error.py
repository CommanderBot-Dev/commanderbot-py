from dataclasses import dataclass
from typing import Any

from commanderbot.ext.automod.condition import Condition, ConditionBase
from commanderbot.ext.automod.event import Event


@dataclass
class ThrowError(ConditionBase):
    """
    Throw an error when checking the condition.

    Intended for testing and debugging.

    Attributes
    ----------
    error
        A human-readable error message.
    """

    error: str

    async def check(self, event: Event) -> bool:
        raise Exception(self.error)


def create_condition(data: Any) -> Condition:
    return ThrowError.from_data(data)
