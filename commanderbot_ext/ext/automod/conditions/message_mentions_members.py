from dataclasses import dataclass

from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class MessageMentionsMembers(AutomodConditionBase):
    async def check(self, event: AutomodEvent) -> bool:
        message = event.message
        # Short-circuit if there's no message or the message is empty.
        if not (message and message.content):
            return False
        # Short-circuit if the message does not mention any members.
        if not message.mentions:
            return False
        member_names = {f"{member}" for member in message.mentions}
        mentioned_members_str = "`" + "` `".join(member_names) + "`"
        event.set_metadata("mentioned_members", mentioned_members_str)
        return True


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageMentionsMembers.from_data(data)
