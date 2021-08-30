from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Type, TypeVar

from discord import Member

from commanderbot_ext.ext.automod.automod_condition import AutomodConditionBase
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject
from commanderbot_ext.lib.utils import timedelta_from_field_optional

ST = TypeVar("ST")


@dataclass
class TargetAccountAgeBase(AutomodConditionBase):
    more_than: Optional[timedelta] = None
    less_than: Optional[timedelta] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        more_than = timedelta_from_field_optional(data, "more_than")
        less_than = timedelta_from_field_optional(data, "less_than")
        return cls(
            description=data.get("description"),
            more_than=more_than,
            less_than=less_than,
        )

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        raise NotImplementedError()

    async def check(self, event: AutomodEvent) -> bool:
        member = self.get_target(event)
        if member is None:
            return False
        now = datetime.utcnow()
        created_at = member.created_at
        age = now - created_at
        is_older = (self.more_than is None) or (age > self.more_than)
        is_younger = (self.less_than is None) or (age < self.less_than)
        return is_older and is_younger
