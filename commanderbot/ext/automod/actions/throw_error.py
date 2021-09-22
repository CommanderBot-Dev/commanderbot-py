from dataclasses import dataclass
from typing import Any

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent


@dataclass
class ThrowError(ActionBase):
    """
    Throw an error when running the action.

    Intended for testing and debugging.

    Attributes
    ----------
    error
        A human-readable error message.
    """

    error: str

    async def apply(self, event: AutomodEvent):
        raise Exception(self.error)


def create_action(data: Any) -> Action:
    return ThrowError.from_data(data)
