from dataclasses import dataclass
from typing import Optional

from discord import Thread
from discord.channel import TextChannel

from commanderbot.ext.automod.automod_event import AutomodEventBase

__all__ = ("ThreadUpdated",)


@dataclass
class ThreadUpdated(AutomodEventBase):
    _before: Thread
    _after: Thread

    @property
    def channel(self) -> Optional[TextChannel]:
        return self.thread.parent

    @property
    def thread(self) -> Thread:
        return self._after