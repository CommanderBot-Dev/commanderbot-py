from dataclasses import dataclass

from discord import TextChannel, Thread

from commanderbot.ext.automod.automod_event import AutomodEventBase

__all__ = ("GuildChannelUpdated",)


@dataclass
class GuildChannelUpdated(AutomodEventBase):
    _before: TextChannel | Thread
    _after: TextChannel | Thread

    @property
    def channel(self) -> TextChannel | Thread:
        return self._after
