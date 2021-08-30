from dataclasses import dataclass
from datetime import datetime

from discord import Member, TextChannel, Thread

from commanderbot.ext.automod.automod_event import AutomodEventBase

__all__ = ("MemberTyping",)


@dataclass
class MemberTyping(AutomodEventBase):
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
