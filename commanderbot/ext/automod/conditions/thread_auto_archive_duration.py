from dataclasses import dataclass
from typing import Any, Dict, Optional

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.condition import Condition, ConditionBase
from commanderbot.lib.integer_range import IntegerRange


@dataclass
class ThreadAutoArchiveDuration(ConditionBase):
    """
    Passes if the thread's auto archive duration is within the given range.

    Attributes
    ----------
    auto_archive_duration
        The range of the auto archive duration to check.
    """

    auto_archive_duration: IntegerRange

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        auto_archive_duration = IntegerRange.from_field(data, "auto_archive_duration")
        return dict(
            auto_archive_duration=auto_archive_duration,
        )

    async def check(self, event: AutomodEvent) -> bool:
        if thread := event.thread:
            return self.auto_archive_duration.includes(thread.auto_archive_duration)
        return False


def create_condition(data: Any) -> Condition:
    return ThreadAutoArchiveDuration.from_data(data)
