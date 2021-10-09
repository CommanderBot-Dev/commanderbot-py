from dataclasses import dataclass
from typing import Type, TypeVar

from commanderbot.ext.automod.automod_condition import (
    AutomodCondition,
    AutomodConditionBase,
)
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject
from commanderbot.lib.integer_range import IntegerRange

ST = TypeVar("ST")


@dataclass
class ThreadAutoArchiveDuration(AutomodConditionBase):
    """
    Passes if the thread's auto archive duration is within the given range.

    Attributes
    ----------
    auto_archive_duration
        The range of the auto archive duration to check.
    """

    auto_archive_duration: IntegerRange

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        auto_archive_duration = IntegerRange.from_field(data, "auto_archive_duration")
        return cls(
            description=data.get("description"),
            auto_archive_duration=auto_archive_duration,
        )

    async def check(self, event: AutomodEvent) -> bool:
        if thread := event.thread:
            return self.auto_archive_duration.includes(thread.auto_archive_duration)
        return False


def create_condition(data: JsonObject) -> AutomodCondition:
    return ThreadAutoArchiveDuration.from_data(data)
