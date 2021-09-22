from dataclasses import dataclass
from typing import Any, Dict, Optional

from commanderbot.ext.automod import events
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.trigger import Trigger, TriggerBase
from commanderbot.lib import RolesGuard


@dataclass
class MemberUpdated(TriggerBase):
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

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        roles = RolesGuard.from_field_optional(data, "roles")
        return dict(
            roles=roles,
        )

    def ignore_by_role(self, event: AutomodEvent) -> bool:
        if self.roles is None:
            return False
        return self.roles.ignore(event.member)

    async def ignore(self, event: AutomodEvent) -> bool:
        return self.ignore_by_role(event)


def create_trigger(data: Any) -> Trigger:
    return MemberUpdated.from_data(data)
