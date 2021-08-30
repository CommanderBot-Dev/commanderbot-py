from dataclasses import dataclass

from commanderbot.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject


@dataclass
class RemoveAllReactions(AutomodActionBase):
    """
    Remove all reactions from the message in context.
    """

    async def apply(self, event: AutomodEvent):
        if message := event.message:
            await message.clear_reactions()


def create_action(data: JsonObject) -> AutomodAction:
    return RemoveAllReactions.from_data(data)
