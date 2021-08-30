from dataclasses import dataclass
from typing import Optional, TypeVar

from discord import Member

from commanderbot.ext.automod.automod_condition import AutomodCondition
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.conditions.abc.target_account_age_base import (
    TargetAccountAgeBase,
)
from commanderbot.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class AuthorAccountAge(TargetAccountAgeBase):
    """
    Check if the author's account is a certain age.

    Attributes
    ----------
    more_than
        The lower bound to check against, if any.
    less_than
        The upper bound to check against, if any.
    """

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        return event.author


def create_condition(data: JsonObject) -> AutomodCondition:
    return AuthorAccountAge.from_data(data)
