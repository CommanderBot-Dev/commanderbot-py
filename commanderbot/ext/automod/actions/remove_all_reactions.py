from dataclasses import dataclass
from typing import Any

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.event import Event


@dataclass
class RemoveAllReactions(ActionBase):
    """
    Remove all reactions from the message in context.
    """

    async def apply(self, event: Event):
        if message := event.message:
            await message.clear_reactions()


def create_action(data: Any) -> Action:
    return RemoveAllReactions.from_data(data)
