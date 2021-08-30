from dataclasses import dataclass
from typing import Optional

from discord import Member

from commanderbot.ext.automod.actions.abc.add_roles_to_target_base import (
    AddRolesToTargetBase,
)
from commanderbot.ext.automod.automod_action import AutomodAction
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject


@dataclass
class AddRolesToAuthor(AddRolesToTargetBase):
    """
    Add roles to the author in context.

    Attributes
    ----------
    roles
        The roles to add.
    """

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        return event.author


def create_action(data: JsonObject) -> AutomodAction:
    return AddRolesToAuthor.from_data(data)
