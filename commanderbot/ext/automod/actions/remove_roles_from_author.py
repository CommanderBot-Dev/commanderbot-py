from dataclasses import dataclass
from typing import Any, Optional

from discord import Member

from commanderbot.ext.automod.action import Action
from commanderbot.ext.automod.actions.abc.remove_roles_from_target_base import (
    RemoveRolesFromTargetBase,
)
from commanderbot.ext.automod.event import Event


@dataclass
class RemoveRolesFromAuthor(RemoveRolesFromTargetBase):
    """
    Remove roles from the author in context.

    Attributes
    ----------
    roles
        The roles to remove.
    """

    def get_target(self, event: Event) -> Optional[Member]:
        return event.author


def create_action(data: Any) -> Action:
    return RemoveRolesFromAuthor.from_data(data)
