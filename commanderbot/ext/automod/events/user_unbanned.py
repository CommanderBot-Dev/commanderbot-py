from dataclasses import dataclass

from discord import User

from commanderbot.ext.automod.event import EventBase

__all__ = ("UserUnbanned",)


@dataclass
class UserUnbanned(EventBase):
    _user: User

    @property
    def user(self) -> User:
        return self._user
