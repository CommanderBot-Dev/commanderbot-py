from dataclasses import dataclass
from typing import Optional

from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class MessageMentions(AutomodConditionBase):
    async def check(self, event: AutomodEvent) -> bool:
        message = event.message
        # Short-circuit if there's no message or the message is empty.
        if not (message and message.content):
            return False
        # Check if the message pings a user.
        if not message.mentions:
            return False
        member_names = {f"{member}" for member in message.mentions}
        stringified_mentions = "`" + "` `".join(member_names) + "`"
        event.set_metadata("stringified_mentions", stringified_mentions)
        return True


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageMentions.from_data(data)
