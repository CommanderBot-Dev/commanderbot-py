from dataclasses import dataclass, field

from commanderbot_lib.logging import Logger, get_logger
from discord.ext.commands import Bot, Cog


@dataclass
class CogStore:
    """
    Abstracts the data storage and persistence of a particular cog.

    This is intended to be used as a starting point for a class that interfaces with the
    cog's in-memory and/or persistent data, in a way that not need concern itself with
    the underlying database.

    For example: altering an in-memory dict or dataclass as a cache that periodically
    gets serialized and flushed to disk.

    Attributes
    -----------
    bot
        The bot/client instance the cog is attached to.
    cog
        The cog instance this state is attached to.
    log
        A logger named in a uniquely identifiable way.
    """

    bot: Bot
    cog: Cog

    log: Logger = field(init=False)

    def __post_init__(self):
        self.log = get_logger(
            f"{self.cog.qualified_name} ({self.__class__.__name__}#{id(self)})"
        )
