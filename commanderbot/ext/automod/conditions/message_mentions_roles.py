from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from commanderbot.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject, RolesGuard

ST = TypeVar("ST")


@dataclass
class MessageMentionsRoles(AutomodConditionBase):
    """
    Check if the message contains role mentions.

    Attributes
    ----------
    roles
        The roles to match against. If empty, all roles will match.
    """

    roles: Optional[RolesGuard] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        roles = RolesGuard.from_data(data.get("roles", {}))
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
        if self.roles is not None:
            mentioned_roles = self.roles.filter_roles(message.role_mentions)
        else:
            mentioned_roles = message.role_mentions
        if not mentioned_roles:
            return False
        event.set_metadata(
            "mentioned_roles",
            " ".join(role.mention for role in mentioned_roles),
        )
        event.set_metadata(
            "mentioned_role_names",
            " ".join(f"`{role}`" for role in mentioned_roles),
        )
        return True


def create_condition(data: JsonObject) -> AutomodCondition:
    return MessageMentionsRoles.from_data(data)
