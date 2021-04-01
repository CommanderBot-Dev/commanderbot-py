from dataclasses import dataclass, field

from commanderbot_lib.logging import Logger, get_logger
from discord.ext.commands import Bot, Cog


@dataclass
class CogState:
    """
    Encapsulates the state and logic of a particular cog.

    This is intended to be used as a starting point for a class that separates the cog's
    in-memory/persistent state and business logic from its top-level definitions, such
    as event listeners and command definitions.

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
