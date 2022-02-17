from dataclasses import dataclass
from typing import Optional, TypeVar

from discord import Member

from commanderbot.ext.automod.automod_condition import AutomodCondition
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.conditions.abc.target_member_for_base import (
    TargetMemberForBase,
)
from commanderbot.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class AuthorMemberFor(TargetMemberForBase):
    """
    Check if the author has been on the server for a certain amount of time.

    Attributes
    ----------
    at_least
        The lower bound to check against, if any.
    at_most
        The upper bound to check against, if any.
    """

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        return event.author


def create_condition(data: JsonObject) -> AutomodCondition:
    return AuthorMemberFor.from_data(data)
