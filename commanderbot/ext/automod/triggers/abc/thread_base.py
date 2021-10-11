from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from discord import Thread

from commanderbot.ext.automod.event import Event
from commanderbot.ext.automod.trigger import TriggerBase
from commanderbot.lib import ChannelsGuard


class EventWithThread(Event, Protocol):
    thread: Thread


@dataclass
class ThreadBase(TriggerBase):
    parent_channels: Optional[ChannelsGuard] = None

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        parent_channels = ChannelsGuard.from_field_optional(data, "parent_channels")
        return dict(
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
