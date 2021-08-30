from dataclasses import dataclass
from typing import Optional, TypeVar

from discord import Member

from commanderbot.ext.automod.automod_condition import AutomodCondition
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.conditions.abc.target_is_not_bot_base import (
    TargetIsNotBotBase,
)
from commanderbot.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class ActorIsNotBot(TargetIsNotBotBase):
    """
    Check if the actor in context is not a bot.
    """

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        return event.actor


def create_condition(data: JsonObject) -> AutomodCondition:
    return ActorIsNotBot.from_data(data)
