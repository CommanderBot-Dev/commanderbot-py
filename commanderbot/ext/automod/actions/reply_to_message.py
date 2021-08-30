from dataclasses import dataclass

from commanderbot_ext.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class ReplyToMessage(AutomodActionBase):
    """
    Reply to the message in context.

    Attributes
    ----------
    content
        The content of the message to send.
    """

    content: str

    async def apply(self, event: AutomodEvent):
        if message := event.message:
            content = event.format_content(self.content)
            await message.reply(content)


def create_action(data: JsonObject) -> AutomodAction:
    return ReplyToMessage.from_data(data)
