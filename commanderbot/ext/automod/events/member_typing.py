from dataclasses import dataclass
from datetime import datetime

from discord import Member, TextChannel, Thread

from commanderbot.ext.automod.event import EventBase

__all__ = ("MemberTyping",)


@dataclass
class MemberTyping(EventBase):
    _channel: TextChannel | Thread
    _member: Member
    _when: datetime

    @property
    def channel(self) -> TextChannel | Thread:
        return self._channel

    @property
    def actor(self) -> Member:
        return self._member

    @property
    def member(self) -> Member:
        return self._member
