from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.ext.automod.automod_trigger import (
    AutomodTrigger,
    AutomodTriggerBase,
)
from commanderbot_ext.lib import ChannelsGuard, JsonObject, RolesGuard

ST = TypeVar("ST")


@dataclass
class MemberTyping(AutomodTriggerBase):
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

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        channels = ChannelsGuard.from_field_optional(data, "channels")
        roles = RolesGuard.from_field_optional(data, "roles")
        return cls(
            description=data.get("description"),
            channels=channels,
            roles=roles,
        )

    def ignore_by_channel(self, event: AutomodEvent) -> bool:
        if self.channels is None:
            return False
        return self.channels.ignore(event.channel)

    def ignore_by_role(self, event: AutomodEvent) -> bool:
        if self.roles is None:
            return False
        return self.roles.ignore(event.member)

    def ignore(self, event: AutomodEvent) -> bool:
        return self.ignore_by_channel(event) or self.ignore_by_role(event)


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return MemberTyping.from_data(data)
