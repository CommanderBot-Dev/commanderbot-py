from dataclasses import dataclass
from typing import Generic, TypeVar

from discord import Guild

from commanderbot_ext._lib.cog_guild_state import CogGuildState
from commanderbot_ext._lib.cog_guild_state_manager import CogGuildStateManager
from commanderbot_ext._lib.cog_state import CogState

GuildStateType = TypeVar("GuildStateType", bound=CogGuildState)


@dataclass
class GuildPartitionedCogState(CogState, Generic[GuildStateType]):
    """
    Extend to maintain global state in addition to guild-specific sub-states, all for a
    particular cog.

    Implements `__getitem__` as a shortcut to the underlying `CogGuildStateManager`.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    guilds: :class:`CogGuildStateManager`
        A lazily-initialized map of guild states, by guild ID.
    """

    guilds: CogGuildStateManager[GuildStateType]

    def __getitem__(self, key: Guild) -> GuildStateType:
        return self.guilds[key]
