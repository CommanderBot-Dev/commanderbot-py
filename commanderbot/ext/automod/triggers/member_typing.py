from dataclasses import dataclass
from typing import Any, Dict, Optional

from commanderbot.ext.automod import events
from commanderbot.ext.automod.event import Event
from commanderbot.ext.automod.trigger import Trigger, TriggerBase
from commanderbot.lib import ChannelsGuard, RolesGuard


@dataclass
class MemberTyping(TriggerBase):
    """
    Fires when an `on_typing` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_typing

    Attributes
    ----------
    channels
        The channels to match against. If empty, all channels will match.
    roles
        The roles to match against. If empty, all roles will match.
    """

    event_types = (events.MemberTyping,)

    channels: Optional[ChannelsGuard] = None
    roles: Optional[RolesGuard] = None

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        channels = ChannelsGuard.from_field_optional(data, "channels")
        roles = RolesGuard.from_field_optional(data, "roles")
        return dict(
            channels=channels,
            roles=roles,
        )

    def ignore_by_channel(self, event: Event) -> bool:
        if self.channels is None:
            return False
        return self.channels.ignore(event.channel)

    def ignore_by_role(self, event: Event) -> bool:
        if self.roles is None:
            return False
        return self.roles.ignore(event.member)

    async def ignore(self, event: Event) -> bool:
        return self.ignore_by_channel(event) or self.ignore_by_role(event)


def create_trigger(data: Any) -> Trigger:
    return MemberTyping.from_data(data)
