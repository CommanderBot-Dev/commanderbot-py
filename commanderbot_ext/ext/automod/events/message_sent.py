from dataclasses import dataclass

from discord import Member, Message, TextChannel

from commanderbot_ext.ext.automod.automod_event import AutomodEventBase

__all__ = ("MessageSent",)


@dataclass
class MessageSent(AutomodEventBase):
    _message: Message

    @property
    def channel(self) -> TextChannel:
        return self._message.channel

    @property
    def message(self) -> Message:
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
