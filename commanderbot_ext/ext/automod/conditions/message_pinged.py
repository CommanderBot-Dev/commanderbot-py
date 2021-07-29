from dataclasses import dataclass
from typing import Optional

from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class MessagePinged(AutomodConditionBase):
    async def check(self, event: AutomodEvent) -> bool:
        message = event.message
        # Short-circuit if there's no message or the message is empty.
        if not (message and message.content):
            return False
        # Check if the message pings a user.
        if message.mentions:
            event.set_metadata(
                "stringified_mentions", "`" + "` `".join(message.mentions) + "`"
            )
            return True
        return False


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessagePinged.from_data(data)
