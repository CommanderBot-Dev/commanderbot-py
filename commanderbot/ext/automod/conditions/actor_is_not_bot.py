from dataclasses import dataclass
from typing import Any, Optional, TypeVar

from discord import Member

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.condition import Condition
from commanderbot.ext.automod.conditions.abc.target_is_not_bot_base import (
    TargetIsNotBotBase,
)

ST = TypeVar("ST")


@dataclass
class ActorIsNotBot(TargetIsNotBotBase):
    """
    Check if the actor in context is not a bot.
    """

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        return event.actor


def create_condition(data: Any) -> Condition:
    return ActorIsNotBot.from_data(data)
