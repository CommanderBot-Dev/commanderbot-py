from dataclasses import dataclass
from typing import Any, Optional

from discord import Member

from commanderbot.ext.automod.action import Action
from commanderbot.ext.automod.actions.abc.add_roles_to_target_base import (
    AddRolesToTargetBase,
)
from commanderbot.ext.automod.automod_event import AutomodEvent


@dataclass
class AddRolesToActor(AddRolesToTargetBase):
    """
    Add roles to the actor in context.

    Attributes
    ----------
    roles
        The roles to add.
    reason
        The reason why roles were added, if any.
    """

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        return event.actor


def create_action(data: Any) -> Action:
    return AddRolesToActor.from_data(data)
