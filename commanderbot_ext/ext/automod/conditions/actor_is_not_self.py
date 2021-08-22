from dataclasses import dataclass
from typing import Optional, TypeVar

from discord import Member

from commanderbot_ext.ext.automod.automod_condition import AutomodCondition
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.ext.automod.conditions.abc.target_is_not_self_base import (
    TargetIsNotSelfBase,
)
from commanderbot_ext.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class ActorIsNotSelf(TargetIsNotSelfBase):
    """
    Check if the actor in context is not the bot itself.
    """

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        return event.actor


def create_condition(data: JsonObject) -> AutomodCondition:
    return ActorIsNotSelf.from_data(data)
