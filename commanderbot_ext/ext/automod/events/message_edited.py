from dataclasses import dataclass

from discord import Member, TextChannel

from commanderbot_ext.ext.automod.automod_event import AutomodEventBase
from commanderbot_ext.lib.types import TextMessage

__all__ = ("MessageEdited",)


@dataclass
class MessageEdited(AutomodEventBase):
    _before: TextMessage
    _after: TextMessage

    @property
    def channel(self) -> TextChannel:
        return self._after.channel

    @property
    def message(self) -> TextMessage:
        return self._after

    @property
    def author(self) -> Member:
        return self._after.author

    @property
    def actor(self) -> Member:
        return self._after.author

    @property
    def member(self) -> Member:
        return self._after.author
