from dataclasses import dataclass
from typing import Dict, Optional, Type, TypeVar

from discord import Color
from discord.abc import Messageable

from commanderbot_ext.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import ChannelID, JsonObject, ValueFormatter
from commanderbot_ext.lib.utils.colors import color_from_field_optional

ST = TypeVar("ST")


@dataclass
class LogMessage(AutomodActionBase):
    """
    Send a log message.

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
    fields
        A custom set of fields to display as part of the message. The key should
        correspond to an event field, and the value is the title to use for it.
    """

    content: Optional[str] = None
    channel: Optional[ChannelID] = None
    emoji: Optional[str] = None
    color: Optional[Color] = None
    fields: Optional[Dict[str, str]] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        color = color_from_field_optional(data, "color")
        return cls(
            description=data.get("description"),
            content=data.get("content"),
            channel=data.get("channel"),
            emoji=data.get("emoji"),
            color=color,
            fields=data.get("fields"),
        )

    async def resolve_channel(self, event: AutomodEvent) -> Optional[Messageable]:
        if self.channel is not None:
            return event.bot.get_channel(self.channel)
        return event.channel

    async def apply(self, event: AutomodEvent):
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
            await channel.send(content)


def create_action(data: JsonObject) -> AutomodAction:
    return LogMessage.from_data(data)
