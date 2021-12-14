from dataclasses import dataclass

from discord import Thread

from commanderbot.ext.automod.event import EventBase

__all__ = ("ThreadUpdated",)


@dataclass
class ThreadUpdated(EventBase):
    _before: Thread
    _after: Thread

    @property
    def channel(self) -> Thread:
        return self.thread

    @property
    def thread(self) -> Thread:
        return self._after
