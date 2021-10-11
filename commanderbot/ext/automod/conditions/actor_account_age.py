from dataclasses import dataclass
from typing import Any, Optional, TypeVar

from discord import Member

from commanderbot.ext.automod.condition import Condition
from commanderbot.ext.automod.conditions.abc.target_account_age_base import (
    TargetAccountAgeBase,
)
from commanderbot.ext.automod.event import Event

ST = TypeVar("ST")


@dataclass
class ActorAccountAge(TargetAccountAgeBase):
    """
    Check if the actor's account is a certain age.

    Attributes
    ----------
    more_than
        The lower bound to check against, if any.
    less_than
        The upper bound to check against, if any.
    """

    def get_target(self, event: Event) -> Optional[Member]:
        return event.actor


def create_condition(data: Any) -> Condition:
    return ActorAccountAge.from_data(data)
