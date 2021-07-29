from dataclasses import dataclass

from commanderbot_ext.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class SendMessage(AutomodActionBase):
    content: str

    async def apply(self, event: AutomodEvent):
        if channel := event.channel:
            content = event.format_content(self.content)
            await channel.send(content)


def create_action(data: JsonObject) -> AutomodAction:
    return SendMessage.from_data(data)
