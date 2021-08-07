from dataclasses import dataclass, field
from typing import Type, TypeVar

from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.ext.automod.automod_roles_guard import AutomodRolesGuard
from commanderbot_ext.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class MessageMentionsRoles(AutomodConditionBase):
    roles: AutomodRolesGuard = field(default_factory=lambda: AutomodRolesGuard())

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        roles = AutomodRolesGuard.from_data(data.get("roles", {}))
        return cls(
            description=data.get("description"),
            roles=roles,
        )

    async def check(self, event: AutomodEvent) -> bool:
        message = event.message
        # Short-circuit if there's no message or the message is empty.
        if not (message and message.content):
            return False
        # Short-circuit if the message does not mention any roles.
        if not message.role_mentions:
            return False
        # Check if we care about any of the mentioned roles.
        mentioned_roles = self.roles.filter(message.role_mentions)
        if not mentioned_roles:
            return False
        role_names = {f"{role}" for role in mentioned_roles}
        mentioned_role_names = "`" + "` `".join(role_names) + "`"
        event.set_metadata("mentioned_role_names", mentioned_role_names)
        role_mentions = {f"{role.mention}" for role in mentioned_roles}
        mentioned_role_mentions = " ".join(role_mentions)
        event.set_metadata("mentioned_role_mentions", mentioned_role_mentions)
        return True


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageMentionsRoles.from_data(data)
