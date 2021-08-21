from dataclasses import dataclass
from datetime import datetime

from discord import Member, TextChannel

from commanderbot_ext.ext.automod.automod_event import AutomodEventBase

__all__ = ("MemberTyping",)


@dataclass
class MemberTyping(AutomodEventBase):
    _channel: TextChannel
    _member: Member
    _when: datetime

    @property
    def channel(self) -> TextChannel:
        return self._channel

    @property
    def actor(self) -> Member:
        return self._member

    @property
    def member(self) -> Member:
        return self._member
