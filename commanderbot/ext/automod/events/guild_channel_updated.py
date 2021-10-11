from dataclasses import dataclass

from discord import TextChannel, Thread

from commanderbot.ext.automod.event import EventBase

__all__ = ("GuildChannelUpdated",)


@dataclass
class GuildChannelUpdated(EventBase):
    _before: TextChannel | Thread
    _after: TextChannel | Thread

    @property
    def channel(self) -> TextChannel | Thread:
        return self._after
