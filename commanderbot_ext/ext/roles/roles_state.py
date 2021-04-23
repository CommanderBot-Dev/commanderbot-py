from dataclasses import dataclass

from commanderbot_ext.ext.roles.roles_guild_state import RolesGuildState
from commanderbot_ext.ext.roles.roles_store import RolesStore
from commanderbot_ext.lib import GuildPartitionedCogState


@dataclass
class RolesState(GuildPartitionedCogState[RolesGuildState]):
    """
    Encapsulates the state and logic of the roles cog, for each guild.

    But since there isn't currently any global state pertaining to the roles cog, this
    class is basically just a wrapper around the `CogGuildStateManager`.
    """

    store: RolesStore
