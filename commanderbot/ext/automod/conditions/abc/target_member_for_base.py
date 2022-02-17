from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, Type, TypeVar

from discord import Member

from commanderbot.ext.automod.automod_condition import AutomodConditionBase
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject
from commanderbot.lib.utils import timedelta_from_field_optional, utcnow_aware

ST = TypeVar("ST")


@dataclass
class TargetMemberForBase(AutomodConditionBase):
    at_least: Optional[timedelta] = None
    at_most: Optional[timedelta] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        at_least = timedelta_from_field_optional(data, "at_least")
        at_most = timedelta_from_field_optional(data, "at_most")
        return cls(
            description=data.get("description"),
            at_least=at_least,
            at_most=at_most,
        )

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        raise NotImplementedError()

    async def check(self, event: AutomodEvent) -> bool:
        member = self.get_target(event)
        if member is None:
            return False
        now = utcnow_aware()
        joined_at = member.joined_at
        if not joined_at:
            return False
        member_for = now - joined_at
        is_at_least = (self.at_least is None) or (member_for > self.at_least)
        is_at_most = (self.at_most is None) or (member_for < self.at_most)
        return is_at_least and is_at_most
