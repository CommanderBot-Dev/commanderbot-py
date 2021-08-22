from dataclasses import dataclass
from typing import Optional, TypeVar

from discord import Member

from commanderbot_ext.ext.automod.automod_condition import AutomodConditionBase
from commanderbot_ext.ext.automod.automod_event import AutomodEvent

ST = TypeVar("ST")


@dataclass
class TargetIsNotBotBase(AutomodConditionBase):
    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        raise NotImplementedError()

    async def check(self, event: AutomodEvent) -> bool:
        if member := self.get_target(event):
            return not member.bot
        return True
