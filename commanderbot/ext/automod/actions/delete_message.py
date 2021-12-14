from dataclasses import dataclass
from typing import Any

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.event import Event


@dataclass
class DeleteMessage(ActionBase):
    """
    Delete the message in context.
    """

    async def apply(self, event: Event):
        if message := event.message:
            await message.delete()


def create_action(data: Any) -> Action:
    return DeleteMessage.from_data(data)
