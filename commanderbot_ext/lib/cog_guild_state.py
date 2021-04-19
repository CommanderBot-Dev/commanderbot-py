from dataclasses import dataclass, field
from logging import Logger, getLogger

from discord import Guild
from discord.ext.commands import Bot, Cog

__all__ = ("CogGuildState",)


@dataclass
class CogGuildState:
    """
    Encapsulates the state and logic of a particular cog, at the guild level.

    This is a thin abstraction that affords us two main conveniences:
    1. keeping guild-based logic separate from global logic; and
    2. keeping the state of each guild isolated from one another.

    Attributes
    -----------
    bot
        The bot/client instance the cog is attached to.
    cog
        The cog instance this state is attached to.
    guild
        The guild instance being managed.
    log
        A logger named in a uniquely identifiable way.
    """

    bot: Bot
    cog: Cog
    guild: Guild

    log: Logger = field(init=False)

    def __post_init__(self):
        self.log = getLogger(
            f"{self.cog.qualified_name}@{self.guild}"
            + f" ({self.__class__.__name__}#{id(self)})"
        )
