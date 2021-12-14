from dataclasses import dataclass
from typing import Any, Dict, Optional

from discord import Member

from commanderbot.ext.automod.condition import ConditionBase
from commanderbot.ext.automod.event import Event
from commanderbot.lib.guards.roles_guard import RolesGuard


@dataclass
class TargetRolesBase(ConditionBase):
    roles: RolesGuard

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        roles = RolesGuard.from_field(data, "roles")
        return dict(
            roles=roles,
        )

    def get_target(self, event: Event) -> Optional[Member]:
        raise NotImplementedError()

    async def check(self, event: Event) -> bool:
        if member := self.get_target(event):
            return not self.roles.ignore(member)
        return False
