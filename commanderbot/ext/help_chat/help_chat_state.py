from dataclasses import dataclass

from commanderbot.ext.help_chat.help_chat_guild_state import HelpChatGuildState
from commanderbot.ext.help_chat.help_chat_store import HelpChatStore
from commanderbot.lib import GuildPartitionedCogState


@dataclass
class HelpChatState(GuildPartitionedCogState[HelpChatGuildState]):
    """
    Encapsulates the state and logic of the help-chat cog, for each guild.
    """

    store: HelpChatStore
