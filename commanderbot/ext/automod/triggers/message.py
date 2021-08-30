from dataclasses import dataclass
from typing import List, Optional, Type, TypeVar

from commanderbot.ext.automod import events
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.automod_trigger import (
    AutomodTrigger,
    AutomodTriggerBase,
)
from commanderbot.lib import ChannelsGuard, JsonObject, RolesGuard

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
    content
        The exact message content to match. If provided, the message must match one of
        these strings exactly. For more complex/flexible matching logic, consider using
        the `message_content_contains` or `message_content_matches` conditions.
    channels
        The channels to match against. If empty, all channels will match.
    author_roles
        The author roles to match against. If empty, all roles will match.
    """

    event_types = (events.MessageSent, events.MessageEdited)

    content: Optional[List[str]] = None
    channels: Optional[ChannelsGuard] = None
    author_roles: Optional[RolesGuard] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        content = data.get("content")
        if isinstance(content, str):
            content = [content]
        channels = ChannelsGuard.from_field_optional(data, "channels")
        author_roles = RolesGuard.from_field_optional(data, "author_roles")
        return cls(
            description=data.get("description"),
            content=content,
            channels=channels,
            author_roles=author_roles,
        )

    def ignore_by_content(self, event: AutomodEvent) -> bool:
        if (self.content is None) or (event.message is None):
            return False
        return event.message.content not in self.content

    def ignore_by_channel(self, event: AutomodEvent) -> bool:
        if self.channels is None:
            return False
        return self.channels.ignore(event.channel)

    def ignore_by_author_role(self, event: AutomodEvent) -> bool:
        if self.author_roles is None:
            return False
        return self.author_roles.ignore(event.author)

    def ignore(self, event: AutomodEvent) -> bool:
        return (
            self.ignore_by_content(event)
            or self.ignore_by_channel(event)
            or self.ignore_by_author_role(event)
        )


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return Message.from_data(data)
