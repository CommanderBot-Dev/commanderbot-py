from dataclasses import dataclass

from discord import Member

from commanderbot.ext.automod.event import EventBase

__all__ = ("MemberLeft",)


@dataclass
class MemberLeft(EventBase):
    _member: Member

    @property
    def member(self) -> Member:
        return self._member
