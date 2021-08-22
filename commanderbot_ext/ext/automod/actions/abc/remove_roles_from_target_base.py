from dataclasses import dataclass
from typing import Optional, Tuple

from discord import Guild, Member

from commanderbot_ext.ext.automod.automod_action import AutomodActionBase
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import RoleID


@dataclass
class RemoveRolesFromTargetBase(AutomodActionBase):
    roles: Tuple[RoleID]

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        raise NotImplementedError()

    async def apply(self, event: AutomodEvent):
        if member := self.get_target(event):
            guild: Guild = member.guild
            roles = [guild.get_role(role_id) for role_id in self.roles]
            await member.remove_roles(roles)
