from dataclasses import dataclass
from typing import Optional, TypeVar

from discord import Member

from commanderbot.ext.automod.automod_condition import AutomodConditionBase
from commanderbot.ext.automod.automod_event import AutomodEvent

ST = TypeVar("ST")


@dataclass
class TargetIsSelfBase(AutomodConditionBase):
    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        raise NotImplementedError()

    async def check(self, event: AutomodEvent) -> bool:
        if member := self.get_target(event):
            return member.id == event.bot.user.id
        return False
