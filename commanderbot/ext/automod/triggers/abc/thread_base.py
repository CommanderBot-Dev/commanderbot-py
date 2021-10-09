from dataclasses import dataclass
from typing import Optional, Protocol, Type, TypeVar

from discord import Thread

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.automod_trigger import AutomodTriggerBase
from commanderbot.lib import ChannelsGuard, JsonObject

ST = TypeVar("ST")


class EventWithThread(AutomodEvent, Protocol):
    thread: Thread


@dataclass
class ThreadBase(AutomodTriggerBase):
    parent_channels: Optional[ChannelsGuard] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        parent_channels = ChannelsGuard.from_field_optional(data, "parent_channels")
        return cls(
            description=data.get("description"),
            parent_channels=parent_channels,
        )

    def ignore(self, event: EventWithThread) -> bool:
        # If no parent channels are defined, don't ignore the thread.
        if self.parent_channels is None:
            return False

        # If the thread has no parent, ignore it.
        if not event.thread.parent:
            return True

        # Otherwise, ignore the thread according to its parent.
        return self.parent_channels.ignore(event.thread.parent)
