from dataclasses import dataclass
from typing import Optional, TypeVar

from discord import Member

from commanderbot.ext.automod.condition import ConditionBase
from commanderbot.ext.automod.event import Event

ST = TypeVar("ST")


@dataclass
class TargetIsNotBotBase(ConditionBase):
    def get_target(self, event: Event) -> Optional[Member]:
        raise NotImplementedError()

    async def check(self, event: Event) -> bool:
        if member := self.get_target(event):
            return not member.bot
        return True
