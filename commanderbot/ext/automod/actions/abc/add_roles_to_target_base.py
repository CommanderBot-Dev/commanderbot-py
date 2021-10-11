from dataclasses import dataclass
from typing import Optional, Tuple

from discord import Guild, Member

from commanderbot.ext.automod.action import ActionBase
from commanderbot.ext.automod.event import Event
from commanderbot.lib import RoleID


@dataclass
class AddRolesToTargetBase(ActionBase):
    roles: Tuple[RoleID]
    reason: Optional[str] = None

    def get_target(self, event: Event) -> Optional[Member]:
        raise NotImplementedError()

    async def apply(self, event: Event):
        if member := self.get_target(event):
            guild: Guild = member.guild
            # TODO Warn about unresolved roles. #logging
            roles = [guild.get_role(role_id) for role_id in self.roles]
            roles = [role for role in roles if role]
            await member.add_roles(*roles, reason=self.reason)
