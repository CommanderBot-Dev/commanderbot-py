from dataclasses import dataclass

from discord import Member, User

from commanderbot.ext.automod.event import EventBase

__all__ = ("UserUpdated",)


@dataclass
class UserUpdated(EventBase):
    _before: User
    _after: User
    _member: Member

    @property
    def member(self) -> Member:
        return self._member
