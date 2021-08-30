from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from discord import Member

from commanderbot_ext.ext.automod.automod_condition import AutomodConditionBase
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject
from commanderbot_ext.lib.guards.roles_guard import RolesGuard

ST = TypeVar("ST")


@dataclass
class TargetRolesBase(AutomodConditionBase):
    roles: RolesGuard

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        roles = RolesGuard.from_field(data, "roles")
        return cls(
            description=data.get("description"),
            roles=roles,
        )

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        raise NotImplementedError()

    async def check(self, event: AutomodEvent) -> bool:
        if member := self.get_target(event):
            return not self.roles.ignore(member)
        return False
