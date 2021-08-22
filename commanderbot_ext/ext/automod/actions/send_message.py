from dataclasses import dataclass
from typing import Optional

from discord.abc import Messageable

from commanderbot_ext.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import ChannelID, JsonObject


@dataclass
class SendMessage(AutomodActionBase):
    """
    Send a message.

    Attributes
    ----------
    content
        The content of the message to send.
    channel
        The channel to send the message in. Defaults to the channel in context.
    """

    content: str

    channel: Optional[ChannelID] = None

    async def resolve_channel(self, event: AutomodEvent) -> Optional[Messageable]:
        if self.channel is not None:
            return event.bot.get_channel(self.channel)
        return event.channel

    async def apply(self, event: AutomodEvent):
        if channel := await self.resolve_channel(event):
            content = event.format_content(self.content)
            await channel.send(content)


def create_action(data: JsonObject) -> AutomodAction:
    return SendMessage.from_data(data)
