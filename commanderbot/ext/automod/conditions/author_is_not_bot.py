from dataclasses import dataclass
from typing import Any, Optional, TypeVar

from discord import Member

from commanderbot.ext.automod.condition import Condition
from commanderbot.ext.automod.conditions.abc.target_is_not_bot_base import (
    TargetIsNotBotBase,
)
from commanderbot.ext.automod.event import Event

ST = TypeVar("ST")


@dataclass
class AuthorIsNotBot(TargetIsNotBotBase):
    """
    Check if the author in context is not a bot.
    """

    def get_target(self, event: Event) -> Optional[Member]:
        return event.author


def create_condition(data: Any) -> Condition:
    return AuthorIsNotBot.from_data(data)
