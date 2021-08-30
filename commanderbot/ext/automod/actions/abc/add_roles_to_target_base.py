from dataclasses import dataclass
from typing import Optional, Tuple

from discord import Guild, Member

from commanderbot.ext.automod.automod_action import AutomodActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import RoleID


@dataclass
class AddRolesToTargetBase(AutomodActionBase):
    roles: Tuple[RoleID]

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        raise NotImplementedError()

    async def apply(self, event: AutomodEvent):
        if member := self.get_target(event):
            guild: Guild = member.guild
            # TODO Warn about unresolved roles. #logging
            roles = [guild.get_role(role_id) for role_id in self.roles]
            roles = [role for role in roles if role]
            await member.add_roles(roles)
