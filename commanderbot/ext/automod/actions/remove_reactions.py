from dataclasses import dataclass
from typing import Any, Tuple

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent


@dataclass
class RemoveReactions(ActionBase):
    """
    Remove certain reactions from the message in context.

    Attributes
    ----------
    reactions
        The reactions to remove.
    """

    reactions: Tuple[str]

    async def apply(self, event: AutomodEvent):
        if message := event.message:
            for reaction in self.reactions:
                await message.clear_reaction(reaction)


def create_action(data: Any) -> Action:
    return RemoveReactions.from_data(data)
