from dataclasses import dataclass

from commanderbot_ext.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class DeleteMessage(AutomodActionBase):
    """
    Delete the message in context.
    """

    async def apply(self, event: AutomodEvent):
        if message := event.message:
            await message.delete()


def create_action(data: JsonObject) -> AutomodAction:
    return DeleteMessage.from_data(data)
