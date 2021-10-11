from dataclasses import dataclass

from discord import TextChannel, Thread

from commanderbot.ext.automod.event import EventBase

__all__ = ("GuildChannelCreated",)


@dataclass
class GuildChannelCreated(EventBase):
    _channel: TextChannel | Thread

    @property
    def channel(self) -> TextChannel | Thread:
        return self._channel
