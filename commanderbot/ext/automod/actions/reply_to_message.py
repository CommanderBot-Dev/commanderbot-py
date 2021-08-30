from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from commanderbot.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import AllowedMentions, JsonObject

ST = TypeVar("ST")


@dataclass
class ReplyToMessage(AutomodActionBase):
    """
    Reply to the message in context.

    Attributes
    ----------
    content
        The content of the message to send.
    allowed_mentions
        The types of mentions allowed in the message. Unless otherwise specified, only
        "everyone" mentions will be suppressed.
    """

    content: str
    allowed_mentions: Optional[AllowedMentions] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        allowed_mentions = AllowedMentions.from_field_optional(data, "allowed_mentions")
        return cls(
            description=data.get("description"),
            content=data.get("content"),
            allowed_mentions=allowed_mentions,
        )

    async def apply(self, event: AutomodEvent):
        if message := event.message:
            content = event.format_content(self.content)
            allowed_mentions = self.allowed_mentions or AllowedMentions.not_everyone()
            await message.reply(
                content,
                allowed_mentions=allowed_mentions,
            )


def create_action(data: JsonObject) -> AutomodAction:
    return ReplyToMessage.from_data(data)
