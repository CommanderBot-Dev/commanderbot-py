from dataclasses import dataclass

from discord import Member

from commanderbot.ext.automod.event import EventBase

__all__ = ("MemberJoined",)


@dataclass
class MemberJoined(EventBase):
    _member: Member

    @property
    def member(self) -> Member:
        return self._member
