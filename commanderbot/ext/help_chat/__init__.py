from discord.ext.commands import Bot

from commanderbot.ext.help_chat.help_chat_cog import HelpChatCog
from commanderbot.core.utils import add_configured_cog


def setup(bot: Bot):
    add_configured_cog(bot, __name__, HelpChatCog)
