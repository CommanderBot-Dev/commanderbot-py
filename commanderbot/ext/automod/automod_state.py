from dataclasses import dataclass

from commanderbot_ext.ext.automod.automod_guild_state import AutomodGuildState
from commanderbot_ext.ext.automod.automod_store import AutomodStore
from commanderbot_ext.lib import GuildPartitionedCogState


@dataclass
class AutomodState(GuildPartitionedCogState[AutomodGuildState]):
    """
    Encapsulates the state and logic of the automod cog, for each guild.
    """

    store: AutomodStore
