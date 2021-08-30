from dataclasses import dataclass

from commanderbot.ext.automod.automod_guild_state import AutomodGuildState
from commanderbot.ext.automod.automod_store import AutomodStore
from commanderbot.lib import GuildPartitionedCogState


@dataclass
class AutomodState(GuildPartitionedCogState[AutomodGuildState]):
    """
    Encapsulates the state and logic of the automod cog, for each guild.
    """

    store: AutomodStore
