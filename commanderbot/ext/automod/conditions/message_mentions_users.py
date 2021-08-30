from dataclasses import dataclass

from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class MessageMentionsUsers(AutomodConditionBase):
    """Check if the message contains user mentions."""

    async def check(self, event: AutomodEvent) -> bool:
        message = event.message
        # Short-circuit if there's no message or the message is empty.
        if not (message and message.content):
            return False
        # Short-circuit if the message does not mention any users.
        if not message.mentions:
            return False
        user_names = {f"{user}" for user in message.mentions}
        mentioned_users_str = "`" + "` `".join(user_names) + "`"
        event.set_metadata("mentioned_users", mentioned_users_str)
        return True


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageMentionsUsers.from_data(data)
