from dataclasses import dataclass
from typing import Optional

from discord import Member

from commanderbot_ext.ext.automod.actions.abc.add_roles_to_target_base import (
    AddRolesToTargetBase,
)
from commanderbot_ext.ext.automod.automod_action import AutomodAction
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class AddRolesToActor(AddRolesToTargetBase):
    """
    Add roles to the actor in context.

    Attributes
    ----------
    roles
        The roles to add.
    """

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        return event.actor


def create_action(data: JsonObject) -> AutomodAction:
    return AddRolesToActor.from_data(data)
