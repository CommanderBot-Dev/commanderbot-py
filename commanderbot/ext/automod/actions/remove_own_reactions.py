from dataclasses import dataclass
from typing import Any, Tuple

from discord import User

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.event import Event


@dataclass
class RemoveOwnReactions(ActionBase):
    """
    Remove the bot's own reactions from the message in context.

    Attributes
    ----------
    reactions
        The reactions to remove.
    """

    reactions: Tuple[str]

    async def apply(self, event: Event):
        if message := event.message:
            bot_user = event.bot.user
            assert isinstance(bot_user, User)
            for reaction in self.reactions:
                await message.remove_reaction(reaction, member=bot_user)


def create_action(data: Any) -> Action:
    return RemoveOwnReactions.from_data(data)
