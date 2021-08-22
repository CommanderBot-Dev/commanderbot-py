from dataclasses import dataclass
from typing import Tuple

from commanderbot_ext.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class AddReactions(AutomodActionBase):
    """
    Add reactions to the message in context.

    Attributes
    ----------
    reactions
        The reactions to add.
    """

    reactions: Tuple[str]

    async def apply(self, event: AutomodEvent):
        if message := event.message:
            for reaction in self.reactions:
                await message.add_reaction(reaction)


def create_action(data: JsonObject) -> AutomodAction:
    return AddReactions.from_data(data)
