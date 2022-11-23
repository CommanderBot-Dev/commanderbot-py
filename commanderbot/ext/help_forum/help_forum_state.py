from dataclasses import dataclass

from commanderbot.ext.help_forum.help_forum_guild_state import HelpForumGuildState
from commanderbot.ext.help_forum.help_forum_store import HelpForumStore
from commanderbot.lib import GuildPartitionedCogState


@dataclass
class HelpForumState(GuildPartitionedCogState[HelpForumGuildState]):
    """
    Encapsulates the state and logic of the help forum cog, for each guild.
    """

    store: HelpForumStore
