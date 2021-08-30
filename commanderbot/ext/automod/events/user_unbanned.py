from dataclasses import dataclass

from discord import User

from commanderbot.ext.automod.automod_event import AutomodEventBase

__all__ = ("UserUnbanned",)


@dataclass
class UserUnbanned(AutomodEventBase):
    _user: User

    @property
    def user(self) -> User:
        return self._user
