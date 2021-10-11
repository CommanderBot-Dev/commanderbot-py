from dataclasses import dataclass

from discord import Member

from commanderbot.ext.automod.event import EventBase

__all__ = ("MemberUpdated",)


@dataclass
class MemberUpdated(EventBase):
    _before: Member
    _after: Member

    @property
    def actor(self) -> Member:
        return self._after

    @property
    def member(self) -> Member:
        return self._after
