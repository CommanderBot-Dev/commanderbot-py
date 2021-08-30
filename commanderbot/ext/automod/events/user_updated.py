from dataclasses import dataclass

from discord import Member, User

from commanderbot_ext.ext.automod.automod_event import AutomodEventBase

__all__ = ("UserUpdated",)


@dataclass
class UserUpdated(AutomodEventBase):
    _before: User
    _after: User
    _member: Member

    @property
    def member(self) -> Member:
        return self._member
