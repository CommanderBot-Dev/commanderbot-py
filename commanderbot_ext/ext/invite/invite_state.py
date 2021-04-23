from dataclasses import dataclass

from commanderbot_ext.ext.invite.invite_guild_state import InviteGuildState
from commanderbot_ext.ext.invite.invite_store import InviteStore
from commanderbot_ext.lib import GuildPartitionedCogState


@dataclass
class InviteState(GuildPartitionedCogState[InviteGuildState]):
    """
    Encapsulates the state and logic of the invite cog, for each guild.
    """

    store: InviteStore
