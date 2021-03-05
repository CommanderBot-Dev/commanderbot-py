from dataclasses import dataclass, field

from commanderbot_lib.logging import Logger, get_logger
from discord.ext.commands import Bot, Cog


@dataclass
class CogStore:
    """
    Manages and operates on the data of a particular cog.

    This is an abstraction layer between the cog's state and its underlying data, be it
    a simple dict or dataclass, a JSON file, or a full-blown database connection.

    This is a stub class that can be extended with common behaviour or operations
    specific to a particular cog. For example: altering an in-memory dict or dataclass
    as a cache that periodically gets serialized and flushed to disk.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    """

    bot: Bot
    cog: Cog

    log: Logger = field(init=False)

    def __post_init__(self):
        self.log = get_logger(
            f"{self.cog.qualified_name} ({self.__class__.__name__}#{id(self)})"
        )
