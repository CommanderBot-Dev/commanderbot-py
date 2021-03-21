from dataclasses import dataclass, field

from commanderbot_lib.logging import Logger, get_logger
from discord import Guild
from discord.ext.commands import Bot, Cog


@dataclass
class CogGuildState:
    """
    Extend to maintain guild-specific state for a particular cog.

    This is a thin abstraction that affords us two main conveniences:
    1. keeping guild-based logic separate from global logic; and
    2. keeping the state of each guild isolated from one another.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    guild: :class:`Guild`
        The discord.py guild being managed.
    """

    bot: Bot
    cog: Cog
    guild: Guild

    log: Logger = field(init=False)

    def __post_init__(self):
        self.log = get_logger(
            f"{self.cog.qualified_name}@{self.guild}"
            + f" ({self.__class__.__name__}#{id(self)})"
        )
