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
class Message(AutomodTriggerBase):
    """
    Fires when an `on_message` or `on_message_edit` event is received.

    See:
    - https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_message
    - https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_message_edit

    Attributes
    ----------
    channels
        The channels to match against. If empty, all channels will match.
    author_roles
        The author roles to match against. If empty, all roles will match.
    """

    event_types = (events.MessageSent, events.MessageEdited)

    channels: Optional[ChannelsGuard] = None
    author_roles: Optional[RolesGuard] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        channels = ChannelsGuard.from_field_optional(data, "channels")
        author_roles = RolesGuard.from_field_optional(data, "author_roles")
        return cls(
            description=data.get("description"),
            channels=channels,
            author_roles=author_roles,
        )

    def ignore_by_channel(self, event: AutomodEvent) -> bool:
        if self.channels is None:
            return False
        return self.channels.ignore(event.channel)

    def ignore_by_author_role(self, event: AutomodEvent) -> bool:
        if self.author_roles is None:
            return False
        return self.author_roles.ignore(event.author)

    def ignore(self, event: AutomodEvent) -> bool:
        return self.ignore_by_channel(event) or self.ignore_by_author_role(event)


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return Message.from_data(data)
