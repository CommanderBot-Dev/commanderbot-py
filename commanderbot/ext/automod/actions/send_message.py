from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, Type, TypeVar

from discord.abc import Messageable

from commanderbot.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import AllowedMentions, ChannelID, JsonObject
from commanderbot.lib.utils import timedelta_from_field_optional

ST = TypeVar("ST")


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

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        allowed_mentions = AllowedMentions.from_field_optional(data, "allowed_mentions")
        delete_after = timedelta_from_field_optional(data, "delete_after")
        return cls(
            description=data.get("description"),
            content=data.get("content"),
            channel=data.get("channel"),
            allowed_mentions=allowed_mentions,
            delete_after=delete_after,
        )

    async def resolve_channel(self, event: AutomodEvent) -> Optional[Messageable]:
        if self.channel is not None:
            return event.bot.get_channel(self.channel)
        return event.channel

    async def apply(self, event: AutomodEvent):
        if channel := await self.resolve_channel(event):
            content = event.format_content(self.content)
            allowed_mentions = self.allowed_mentions or AllowedMentions.not_everyone()
            params = dict(
                allowed_mentions=allowed_mentions,
            )
            if self.delete_after is not None:
                params.update(delete_after=self.delete_after.total_seconds())
            await channel.send(content, **params)


def create_action(data: JsonObject) -> AutomodAction:
    return SendMessage.from_data(data)
