from dataclasses import dataclass, field
from logging import Logger, getLogger
from typing import Callable, Dict, Generic, Iterable, TypeVar, Union

from discord import Guild
from discord.ext.commands import Bot, Cog

from commanderbot_ext.lib.cog_guild_state import CogGuildState
from commanderbot_ext.lib.types import GuildID

__all__ = ("CogGuildStateManager",)


GuildStateType = TypeVar("GuildStateType", bound=CogGuildState)


@dataclass
class CogGuildStateManager(Generic[GuildStateType]):
    """
    A glorified dictionary that handles the lazy-initialization of guild states.

    Attributes
    ----------
    bot
        The bot/client instance the cog is attached to.
    cog
        The cog instance this state is attached to.
    factory
        A callable object that creates new guild states.

        There are several ways to provide such an object:
        1. a lambda, function, or bound method with a matching signature; or
        2. an instance of a class that implements `__call__` with a matching signature.
    log
        A logger named in a uniquely identifiable way.
    """

    bot: Bot
    cog: Cog
    factory: Callable[[Guild], GuildStateType]

    log: Logger = field(init=False)

    _state_by_id: Dict[GuildID, GuildStateType] = field(init=False)

    def __post_init__(self):
        self.log = getLogger(
            f"{self.cog.qualified_name} ({self.__class__.__name__}#{id(self)})"
        )
        self._state_by_id = {}

    def __getitem__(self, key: Union[Guild, GuildID]) -> GuildStateType:
        return self.get(key)

    @property
    def available(self) -> Iterable[GuildStateType]:
        yield from self._state_by_id.values()

    def _set_state(self, guild: Guild, state: GuildStateType):
        self.log.debug(f"Setting state for guild: {guild}")
        if guild.id in self._state_by_id:
            raise KeyError(f"Attempted to overwrite state for guild: {guild}")
        self._state_by_id[guild.id] = state

    def _init_state(self, guild: Guild) -> GuildStateType:
        self.log.debug(f"Initializing state for guild: {guild}")
        guild_state = self.factory(guild)
        self._set_state(guild, guild_state)
        return guild_state

    def get(self, key: Union[Guild, GuildID]) -> GuildStateType:
        # Lazily-initialize guild states as they are accessed.
        guild = key if isinstance(key, Guild) else self.bot.get_guild(key)
        if not guild:
            raise ValueError(f"Unable to initialize state for unknown guild: {key}")
        guild_state = self._state_by_id.get(guild.id)
        if guild_state is None:
            guild_state = self._init_state(guild)
        return guild_state
