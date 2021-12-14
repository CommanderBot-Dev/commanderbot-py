from dataclasses import dataclass
from typing import Any, Optional, TypeVar

from discord import Member

from commanderbot.ext.automod.condition import Condition
from commanderbot.ext.automod.conditions.abc.target_is_not_self_base import (
    TargetIsNotSelfBase,
)
from commanderbot.ext.automod.event import Event

ST = TypeVar("ST")


@dataclass
class AuthorIsNotSelf(TargetIsNotSelfBase):
    """
    Check if the author in context is not the bot itself.
    """

    def get_target(self, event: Event) -> Optional[Member]:
        return event.author


def create_condition(data: Any) -> Condition:
    return AuthorIsNotSelf.from_data(data)
