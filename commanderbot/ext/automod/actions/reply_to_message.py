from dataclasses import dataclass
from typing import Any, Dict, Optional

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import AllowedMentions


@dataclass
class ReplyToMessage(ActionBase):
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

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_mentions = AllowedMentions.from_field_optional(data, "allowed_mentions")
        return dict(
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


def create_action(data: Any) -> Action:
    return ReplyToMessage.from_data(data)
