from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, Optional

from discord.abc import Messageable

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.event import Event
from commanderbot.lib import AllowedMentions, ChannelID
from commanderbot.lib.utils import timedelta_from_field_optional


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
    delete_after
        The amount of time to delete the message after, if at all.
    """

    content: str
    channel: Optional[ChannelID] = None
    allowed_mentions: Optional[AllowedMentions] = None
    delete_after: Optional[timedelta] = None

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_mentions = AllowedMentions.from_field_optional(data, "allowed_mentions")
        delete_after = timedelta_from_field_optional(data, "delete_after")
        return dict(
            allowed_mentions=allowed_mentions,
            delete_after=delete_after,
        )

    async def resolve_channel(self, event: Event) -> Optional[Messageable]:
        if self.channel is not None:
            channel = event.bot.get_channel(self.channel)
            assert isinstance(channel, Messageable)
            return channel
        return event.channel

    async def apply(self, event: Event):
        if channel := await self.resolve_channel(event):
            content = event.format_content(self.content)
            allowed_mentions = self.allowed_mentions or AllowedMentions.not_everyone()
            params = dict(
                allowed_mentions=allowed_mentions,
            )
            if self.delete_after is not None:
                params.update(delete_after=self.delete_after.total_seconds())
            await channel.send(content, **params)


def create_action(data: Any) -> Action:
    return SendMessage.from_data(data)
