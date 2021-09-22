from dataclasses import dataclass
from typing import Any, Dict, Optional

from discord.abc import Messageable

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import AllowedMentions, ChannelID


@dataclass
class SendMessage(ActionBase):
    """
    Send a message.

    Attributes
    ----------
    content
        The content of the message to send.
    channel
        The channel to send the message in. Defaults to the channel in context.
    allowed_mentions
        The types of mentions allowed in the message. Unless otherwise specified, only
        "everyone" mentions will be suppressed.
    """

    content: str
    channel: Optional[ChannelID] = None
    allowed_mentions: Optional[AllowedMentions] = None

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_mentions = AllowedMentions.from_field_optional(data, "allowed_mentions")
        return dict(
            allowed_mentions=allowed_mentions,
        )

    async def resolve_channel(self, event: AutomodEvent) -> Optional[Messageable]:
        if self.channel is not None:
            channel = event.bot.get_channel(self.channel)
            assert isinstance(channel, Messageable)
            return channel
        return event.channel

    async def apply(self, event: AutomodEvent):
        if channel := await self.resolve_channel(event):
            content = event.format_content(self.content)
            allowed_mentions = self.allowed_mentions or AllowedMentions.not_everyone()
            await channel.send(
                content,
                allowed_mentions=allowed_mentions,
            )


def create_action(data: Any) -> Action:
    return SendMessage.from_data(data)
