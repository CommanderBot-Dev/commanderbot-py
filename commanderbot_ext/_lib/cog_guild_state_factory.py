from abc import abstractmethod
from typing import Protocol, TypeVar

from discord import Guild

from commanderbot_ext._lib.cog_guild_state import CogGuildState

GuildStateType = TypeVar("GuildStateType", bound=CogGuildState)


class CogGuildStateFactory(Protocol[GuildStateType]):
    """
    An arbitrary callable object that creates new guild states.

    This is an implicit callable interface, and there are two ways to use it:
    1. pass a function with the same signature as `__call__`; or
    2. pass an instance of a class that implements `__call__` with the same signature.
    """

    @abstractmethod
    def __call__(self, guild: Guild) -> GuildStateType:
        ...
