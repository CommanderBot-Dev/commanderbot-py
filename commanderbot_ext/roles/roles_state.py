from dataclasses import dataclass

from commanderbot_ext._lib.guild_partitioned_cog_state import GuildPartitionedCogState
from commanderbot_ext.roles.roles_guild_state import RolesGuildState
from commanderbot_ext.roles.roles_store import RolesStore


@dataclass
class RolesState(GuildPartitionedCogState[RolesGuildState]):
    """
    Encapsulates the state and logic of the roles cog, for each guild.

    But since there isn't currently any global state pertaining to the roles cog, this
    class is basically just a wrapper around the `CogGuildStateManager`.
    """

    store: RolesStore
