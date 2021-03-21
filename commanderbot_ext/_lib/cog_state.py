from dataclasses import dataclass, field

from commanderbot_lib.logging import Logger, get_logger
from discord.ext.commands import Bot, Cog


@dataclass
class CogState:
    """
    Extend to maintain global state for a particular cog.

    The overarching idea here is to keep state separate, as a component of the cog, to
    help clean-up the cog's namespace for other things like listeners and commands.

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
