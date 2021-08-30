from dataclasses import dataclass

from commanderbot.ext.faq.faq_guild_state import FaqGuildState
from commanderbot.ext.faq.faq_store import FaqStore
from commanderbot.lib import GuildPartitionedCogState


@dataclass
class FaqState(GuildPartitionedCogState[FaqGuildState]):
    """
    Encapsulates the state and logic of the FAQ cog, for each guild.
    """

    store: FaqStore
