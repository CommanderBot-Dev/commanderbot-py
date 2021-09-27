from dataclasses import dataclass

from discord import Thread

from commanderbot.ext.automod.automod_event import AutomodEventBase

__all__ = ("ThreadDeleted",)


@dataclass
class ThreadDeleted(AutomodEventBase):
    _thread: Thread

    @property
    def channel(self) -> Thread:
        return self.thread

    @property
    def thread(self) -> Thread:
        return self._thread
