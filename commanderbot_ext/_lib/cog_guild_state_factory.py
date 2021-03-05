from abc import abstractmethod
from typing import Protocol, TypeVar

from discord import Guild

from commanderbot_ext._lib.cog_guild_state import CogGuildState

GuildStateType = TypeVar("GuildStateType", bound=CogGuildState)


class CogGuildStateFactory(Protocol[GuildStateType]):
    @abstractmethod
    def __call__(self, guild: Guild) -> GuildStateType:
        ...
