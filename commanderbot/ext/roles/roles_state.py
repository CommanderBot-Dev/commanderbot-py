from dataclasses import dataclass

from commanderbot.ext.roles.roles_guild_state import RolesGuildState
from commanderbot.ext.roles.roles_store import RolesStore
from commanderbot.lib import GuildPartitionedCogState


@dataclass
class RolesState(GuildPartitionedCogState[RolesGuildState]):
    """
    Encapsulates the state and logic of the roles cog, for each guild.

    But since there isn't currently any global state pertaining to the roles cog, this
    class is basically just a wrapper around the `CogGuildStateManager`.
    """

    store: RolesStore
