from dataclasses import dataclass
from typing import Generic, TypeVar, Union

from discord import Guild

from commanderbot_ext.lib.cog_guild_state import CogGuildState
from commanderbot_ext.lib.cog_guild_state_manager import CogGuildStateManager
from commanderbot_ext.lib.cog_state import CogState
from commanderbot_ext.lib.types import GuildID

__all__ = ("GuildPartitionedCogState",)


GuildStateType = TypeVar("GuildStateType", bound=CogGuildState)


@dataclass
class GuildPartitionedCogState(CogState, Generic[GuildStateType]):
    """
    Encapsulates the state and logic of a particular cog, for each guild.

    This is intended to be used just as `CogState` is, but in addition to maintaining
    several sub-states that each correspond to their own guild. A subclass of
    `CogGuildState` should be defined to implement guild-specific funtionality.

    Uses a `CogGuildStateManager` to manage the lazy-initialization of `CogGuildState`
    instances, and implements `__getitem__` as a shortcut to this.

    Attributes
    -----------
    bot
        The bot/client instance the cog is attached to.
    cog
        The cog instance this state is attached to.
    log
        A logger named in a uniquely identifiable way.
    guilds
        The `CogGuildStateManager` instance to manage guild states.
    """

    guilds: CogGuildStateManager[GuildStateType]

    def __getitem__(self, key: Union[Guild, GuildID]) -> GuildStateType:
        return self.guilds[key]
