from dataclasses import dataclass

from discord import Member, TextChannel, Thread

from commanderbot_ext.ext.automod.automod_event import AutomodEventBase
from commanderbot_ext.lib.types import TextMessage

__all__ = ("MessageSent",)


@dataclass
class MessageSent(AutomodEventBase):
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
