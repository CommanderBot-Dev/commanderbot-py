from dataclasses import dataclass
from typing import Optional, TypeVar

from discord import Member

from commanderbot_ext.ext.automod.automod_condition import AutomodCondition
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.ext.automod.conditions.abc.target_is_not_bot_base import (
    TargetIsNotBotBase,
)
from commanderbot_ext.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class AuthorIsNotBot(TargetIsNotBotBase):
    """
    Check if the author in context is not a bot.
    """

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        return event.author


def create_condition(data: JsonObject) -> AutomodCondition:
    return AuthorIsNotBot.from_data(data)
