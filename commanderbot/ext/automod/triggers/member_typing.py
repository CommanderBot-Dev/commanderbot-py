from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from commanderbot.ext.automod import events
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.automod_trigger import AutomodTrigger, AutomodTriggerBase
from commanderbot.lib import ChannelsGuard, ChannelTypesGuard, JsonObject, RolesGuard

ST = TypeVar("ST")


@dataclass
class MemberTyping(AutomodTriggerBase):
    """
    Fires when an `on_typing` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_typing

    Attributes
    ----------
    channel_types
        The channel types to match against. If empty, all channel types will match.
    channels
        The channels to match against. If empty, all channels will match.
    roles
        The roles to match against. If empty, all roles will match.
    """

    event_types = (events.MemberTyping,)

    channel_types: Optional[ChannelTypesGuard] = None
    channels: Optional[ChannelsGuard] = None
    roles: Optional[RolesGuard] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        channel_types = ChannelTypesGuard.from_field_optional(data, "channel_types")
        channels = ChannelsGuard.from_field_optional(data, "channels")
        roles = RolesGuard.from_field_optional(data, "roles")
        return cls(
            description=data.get("description"),
            channel_types=channel_types,
            channels=channels,
            roles=roles,
        )

    def ignore_by_channel_type(self, event: AutomodEvent) -> bool:
        if self.channel_types is None:
            return False
        return self.channel_types.ignore(event.channel)

    def ignore_by_channel(self, event: AutomodEvent) -> bool:
        if self.channels is None:
            return False
        return self.channels.ignore(event.channel)

    def ignore_by_role(self, event: AutomodEvent) -> bool:
        if self.roles is None:
            return False
        return self.roles.ignore(event.member)

    def ignore(self, event: AutomodEvent) -> bool:
        return (
            self.ignore_by_channel_type(event)
            or self.ignore_by_channel(event)
            or self.ignore_by_role(event)
        )


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return MemberTyping.from_data(data)
