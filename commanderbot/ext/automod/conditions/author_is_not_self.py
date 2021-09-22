from dataclasses import dataclass
from typing import Optional, TypeVar

from discord import Member

from commanderbot.ext.automod.condition import Condition
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.conditions.abc.target_is_not_self_base import (
    TargetIsNotSelfBase,
)
from commanderbot.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class AuthorIsNotSelf(TargetIsNotSelfBase):
    """
    Check if the author in context is not the bot itself.
    """

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        return event.author


def create_condition(data: JsonObject) -> Condition:
    return AuthorIsNotSelf.from_data(data)
