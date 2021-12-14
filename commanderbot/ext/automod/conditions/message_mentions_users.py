from dataclasses import dataclass
from typing import Any

from commanderbot.ext.automod.condition import Condition, ConditionBase
from commanderbot.ext.automod.event import Event


@dataclass
class MessageMentionsUsers(ConditionBase):
    """Check if the message contains user mentions."""

    async def check(self, event: Event) -> bool:
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


def create_condition(data: Any) -> Condition:
    return MessageMentionsUsers.from_data(data)
