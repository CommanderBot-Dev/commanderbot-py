from dataclasses import dataclass
from typing import TypeVar

from commanderbot.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class DMMember(AutomodActionBase):
    """
    Send a direct message to the member in question.

    Attributes
    ----------
    content
        The content of the message to send.
    """

    content: str

    async def apply(self, event: AutomodEvent):
        if member := event.member:
            content = event.format_content(self.content)
            await member.send(content)


def create_action(data: JsonObject) -> AutomodAction:
    return DMMember.from_data(data)
