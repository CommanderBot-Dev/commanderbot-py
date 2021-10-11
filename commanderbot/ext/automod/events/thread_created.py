from dataclasses import dataclass

from discord import Thread

from commanderbot.ext.automod.event import EventBase

__all__ = ("ThreadCreated",)


@dataclass
class ThreadCreated(EventBase):
    _thread: Thread

    @property
    def channel(self) -> Thread:
        return self.thread

    @property
    def thread(self) -> Thread:
        return self._thread
