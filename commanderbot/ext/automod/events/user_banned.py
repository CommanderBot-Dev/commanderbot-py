from dataclasses import dataclass

from discord import User

from commanderbot.ext.automod.event import EventBase

__all__ = ("UserBanned",)


@dataclass
class UserBanned(EventBase):
    _user: User

    @property
    def user(self) -> User:
        return self._user
