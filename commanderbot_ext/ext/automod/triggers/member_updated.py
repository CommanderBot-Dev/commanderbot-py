from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.ext.automod.automod_trigger import (
    AutomodTrigger,
    AutomodTriggerBase,
)
from commanderbot_ext.lib import JsonObject, RolesGuard

ST = TypeVar("ST")


@dataclass
class MemberUpdated(AutomodTriggerBase):
    """
    Fires when an `on_typing` event is received.

    This occurs when one or more of the following things change:
    - status
    - activity
    - nickname
    - roles
    - pending

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_typing

    Attributes
    ----------
    roles
        The roles to match against. If empty, all roles will match.
    """

    event_types = (events.MemberUpdated,)

    roles: Optional[RolesGuard] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        roles = RolesGuard.from_field_optional(data, "roles")
        return cls(
            description=data.get("description"),
            roles=roles,
        )

    def ignore_by_role(self, event: AutomodEvent) -> bool:
        if self.roles is None:
            return False
        return self.roles.ignore(event.member)

    def ignore(self, event: AutomodEvent) -> bool:
        return self.ignore_by_role(event)


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return MemberUpdated.from_data(data)
