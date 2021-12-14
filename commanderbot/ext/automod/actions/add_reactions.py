from dataclasses import dataclass
from typing import Any, Tuple

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.event import Event


@dataclass
class AddReactions(ActionBase):
    """
    Add reactions to the message in context.

    Attributes
    ----------
    reactions
        The reactions to add.
    """

    reactions: Tuple[str]

    async def apply(self, event: Event):
        if message := event.message:
            for reaction in self.reactions:
                await message.add_reaction(reaction)


def create_action(data: Any) -> Action:
    return AddReactions.from_data(data)
