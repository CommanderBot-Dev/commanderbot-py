from dataclasses import dataclass

from discord import Member, TextChannel, Thread

from commanderbot.ext.automod.event import EventBase
from commanderbot.lib.types import TextMessage

__all__ = ("MessageFrequencyChanged",)


@dataclass
class MessageFrequencyChanged(EventBase):
    _message: TextMessage

    @property
    def channel(self) -> TextChannel | Thread:
        return self._message.channel

    @property
    def message(self) -> TextMessage:
        return self._message

    @property
    def author(self) -> Member:
        return self._message.author

    @property
    def actor(self) -> Member:
        return self._message.author

    @property
    def member(self) -> Member:
        return self._message.author
