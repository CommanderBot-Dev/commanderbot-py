from dataclasses import dataclass

from commanderbot.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject


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
        event.set_metadata(
            "mentioned_users",
            " ".join(user.mention for user in message.mentions),
        )
        event.set_metadata(
            "mentioned_user_names",
            " ".join(f"`{user}`" for user in message.mentions),
        )
        return True


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageMentionsUsers.from_data(data)
