from dataclasses import dataclass

from discord import Thread

from commanderbot.ext.automod.automod_event import AutomodEventBase

__all__ = ("ThreadUpdated",)


@dataclass
class ThreadUpdated(AutomodEventBase):
    _before: Thread
    _after: Thread

    @property
    def channel(self) -> Thread:
        return self.thread

    @property
    def thread(self) -> Thread:
        return self._after
