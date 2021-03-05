from dataclasses import dataclass, field
from typing import Dict, Generic, Iterable, TypeVar

from commanderbot_lib.logging import Logger, get_logger
from commanderbot_lib.types import GuildID
from discord import Guild
from discord.ext.commands import Bot, Cog

from commanderbot_ext._lib.cog_guild_state import CogGuildState
from commanderbot_ext._lib.cog_guild_state_factory import CogGuildStateFactory

GuildStateType = TypeVar("GuildStateType", bound=CogGuildState)


@dataclass
class CogGuildStateManager(Generic[GuildStateType]):
    """
    A glorified dictionary that handles the lazy-initialization of guild states.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    factory: :class:`CogGuildStateFactory`
        The factory to use in creating new guild states.
    """

    bot: Bot
    cog: Cog
    factory: CogGuildStateFactory[GuildStateType]

    log: Logger = field(init=False)
    _state_by_id: Dict[GuildID, GuildStateType] = field(init=False)

    def __post_init__(self):
        self.log = get_logger(
            f"{self.cog.qualified_name} ({self.__class__.__name__}#{id(self)})"
        )
        self._state_by_id = {}

    def __getitem__(self, key: Guild) -> GuildStateType:
        return self.get(key)

    @property
    def available(self) -> Iterable[GuildStateType]:
        yield from self._state_by_id.values()

    def set_state(self, guild: Guild, state: GuildStateType):
        if guild.id in self._state_by_id:
            raise KeyError(f"Attempted to overwrite state for guild: {guild}")
        self._state_by_id[guild.id] = state

    def init_state(self, guild: Guild) -> GuildStateType:
        self.log.info(f"Initializing state for guild: {guild}")
        guild_state = self.factory(guild)
        self.set_state(guild, guild_state)
        return guild_state

    def get(self, guild: Guild) -> GuildStateType:
        # Lazily-initialize guild states as they are accessed.
        guild_state = self._state_by_id.get(guild.id)
        if guild_state is None:
            guild_state = self.init_state(guild)
        return guild_state
