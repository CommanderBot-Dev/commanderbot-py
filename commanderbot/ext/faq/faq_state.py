from dataclasses import dataclass

from commanderbot_ext.ext.faq.faq_guild_state import FaqGuildState
from commanderbot_ext.ext.faq.faq_store import FaqStore
from commanderbot_ext.lib import GuildPartitionedCogState


@dataclass
class FaqState(GuildPartitionedCogState[FaqGuildState]):
    """
    Encapsulates the state and logic of the FAQ cog, for each guild.
    """

    store: FaqStore
