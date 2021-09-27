from dataclasses import dataclass

from discord import TextChannel, Thread

from commanderbot.ext.automod.automod_event import AutomodEventBase

__all__ = ("GuildChannelCreated",)


@dataclass
class GuildChannelCreated(AutomodEventBase):
    _channel: TextChannel | Thread

    @property
    def channel(self) -> TextChannel | Thread:
        return self._channel
