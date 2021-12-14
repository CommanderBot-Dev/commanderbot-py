from dataclasses import dataclass
from typing import Any, Dict, Optional

from discord import Color
from discord.abc import Messageable

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.event import Event
from commanderbot.lib import AllowedMentions, ChannelID, ValueFormatter
from commanderbot.lib.utils import color_from_field_optional, message_to_file


@dataclass
class LogMessage(ActionBase):
    """
    Send a log message, with pings disabled by default.

    Attributes
    ----------
    content
        The content of the message to send.
    channel
        The channel to send the message in. Defaults to the channel in context.
    emoji
        The emoji used to represent the type of message.
    color
        The emoji used to represent the type of message.
    attach_message
        Whether to attach the message-in-context (as a text file) to the log message.
    fields
        A custom set of fields to display as part of the message. The key should
        correspond to an event field, and the value is the title to use for it.
    allowed_mentions
        The types of mentions allowed in the message. Unless otherwise specified, all
        mentions will be suppressed.
    """

    content: Optional[str] = None
    channel: Optional[ChannelID] = None
    emoji: Optional[str] = None
    color: Optional[Color] = None
    attach_message: Optional[bool] = None
    fields: Optional[Dict[str, str]] = None
    allowed_mentions: Optional[AllowedMentions] = None

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        color = color_from_field_optional(data, "color")
        allowed_mentions = AllowedMentions.from_field_optional(data, "allowed_mentions")
        return dict(
            color=color,
            allowed_mentions=allowed_mentions,
        )

    async def resolve_channel(self, event: Event) -> Optional[Messageable]:
        if self.channel is not None:
            channel = event.bot.get_channel(self.channel)
            assert isinstance(channel, Messageable)
            return channel
        return event.channel

    async def apply(self, event: Event):
        if channel := await self.resolve_channel(event):
            parts = []
            if self.emoji:
                parts.append(self.emoji)
            if self.content:
                formatted_content = event.format_content(self.content)
                parts.append(formatted_content)
            if self.fields:
                event_fields = event.get_fields()
                field_parts = []
                for field_key, field_title in self.fields.items():
                    field_value = event_fields.get(field_key)
                    if isinstance(field_value, ValueFormatter):
                        field_value_str = str(field_value)
                    else:
                        field_value_str = f"`{field_value}`"
                    field_parts.append(f"{field_title} {field_value_str}")
                fields_str = ", ".join(field_parts)
                parts.append(fields_str)
            content = " ".join(parts)
            allowed_mentions = self.allowed_mentions or AllowedMentions.none()
            if self.attach_message and (message := event.message):
                message_file = message_to_file(message)
                await channel.send(
                    content,
                    file=message_file,
                    allowed_mentions=allowed_mentions,
                )
            else:
                await channel.send(content, allowed_mentions=allowed_mentions)


def create_action(data: Any) -> Action:
    return LogMessage.from_data(data)
