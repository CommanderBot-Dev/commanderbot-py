from dataclasses import dataclass
from typing import Optional, TypeVar

from discord import Member

from commanderbot.ext.automod.automod_condition import AutomodCondition
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.conditions.abc.target_is_bot_base import TargetIsBotBase
from commanderbot.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class AuthorIsBot(TargetIsBotBase):
    """
    Check if the author in context is a bot.
    """

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        return event.author


def create_condition(data: JsonObject) -> AutomodCondition:
    return AuthorIsBot.from_data(data)
