from dataclasses import dataclass

from commanderbot_ext._lib.guild_partitioned_cog_state import GuildPartitionedCogState
from commanderbot_ext.roles.roles_guild_state import RolesGuildState
from commanderbot_ext.roles.roles_store import RolesStore


@dataclass
class RolesState(GuildPartitionedCogState[RolesGuildState]):
    """
    Encapsulates the state and logic of the roles cog, for each guild.

    Except there isn't currently any global state pertaining to the roles cog, so
    this class is effetively a wrapper around the `CogGuildStateManager`.
    """

    store: RolesStore
