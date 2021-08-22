from dataclasses import dataclass
from typing import Tuple

from commanderbot_ext.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class RemoveOwnReactions(AutomodActionBase):
    """
    Remove the bot's own reactions from the message in context.

    Attributes
    ----------
    reactions
        The reactions to remove.
    """

    reactions: Tuple[str]

    async def apply(self, event: AutomodEvent):
        if message := event.message:
            for reaction in self.reactions:
                await message.remove_reaction(reaction, member=event.bot.user)


def create_action(data: JsonObject) -> AutomodAction:
    return RemoveOwnReactions.from_data(data)
