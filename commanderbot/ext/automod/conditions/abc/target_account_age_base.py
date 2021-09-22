from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, Optional

from discord import Member

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.condition import ConditionBase
from commanderbot.lib.utils import timedelta_from_field_optional, utcnow_aware


@dataclass
class TargetAccountAgeBase(ConditionBase):
    more_than: Optional[timedelta] = None
    less_than: Optional[timedelta] = None

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        more_than = timedelta_from_field_optional(data, "more_than")
        less_than = timedelta_from_field_optional(data, "less_than")
        return dict(
            more_than=more_than,
            less_than=less_than,
        )

    def get_target(self, event: AutomodEvent) -> Optional[Member]:
        raise NotImplementedError()

    async def check(self, event: AutomodEvent) -> bool:
        member = self.get_target(event)
        if member is None:
            return False
        now = utcnow_aware()
        created_at = member.created_at
        age = now - created_at
        is_older = (self.more_than is None) or (age > self.more_than)
        is_younger = (self.less_than is None) or (age < self.less_than)
        return is_older and is_younger
