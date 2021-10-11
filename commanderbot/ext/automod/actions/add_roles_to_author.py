from dataclasses import dataclass
from typing import Any, Optional

from discord import Member

from commanderbot.ext.automod.action import Action
from commanderbot.ext.automod.actions.abc.add_roles_to_target_base import (
    AddRolesToTargetBase,
)
from commanderbot.ext.automod.event import Event


@dataclass
class AddRolesToAuthor(AddRolesToTargetBase):
    """
    Add roles to the author in context.

    Attributes
    ----------
    roles
        The roles to add.
    reason
        The reason why roles were added, if any.
    """

    def get_target(self, event: Event) -> Optional[Member]:
        return event.author


def create_action(data: Any) -> Action:
    return AddRolesToAuthor.from_data(data)
