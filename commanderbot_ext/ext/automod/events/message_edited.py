from dataclasses import dataclass

from discord import Member, Message, TextChannel

from commanderbot_ext.ext.automod.automod_event import AutomodEventBase

__all__ = ("MessageEdited",)


@dataclass
class MessageEdited(AutomodEventBase):
    _before: Message
    _after: Message

    @property
    def channel(self) -> TextChannel:
        return self._after.channel

    @property
    def message(self) -> Message:
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
