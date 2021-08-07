from dataclasses import dataclass, field
from typing import Type, TypeVar

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_channels_guard import AutomodChannelsGuard
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.ext.automod.automod_roles_guard import AutomodRolesGuard
from commanderbot_ext.ext.automod.automod_trigger import (
    AutomodTrigger,
    AutomodTriggerBase,
)
from commanderbot_ext.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class Message(AutomodTriggerBase):
    event_types = (events.MessageSent, events.MessageEdited)

    channels: AutomodChannelsGuard = field(
        default_factory=lambda: AutomodChannelsGuard()
    )
    roles: AutomodRolesGuard = field(default_factory=lambda: AutomodRolesGuard())

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        channels = AutomodChannelsGuard.from_data(data.get("channels", {}))
        roles = AutomodRolesGuard.from_data(data.get("roles", {}))
        return cls(
            description=data.get("description"),
            channels=channels,
            roles=roles,
        )

    def ignore(self, event: AutomodEvent) -> bool:
        return self.channels.ignore(event) or self.roles.ignore(event)


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return Message.from_data(data)
