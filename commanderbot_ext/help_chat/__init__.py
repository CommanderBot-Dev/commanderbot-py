from commanderbot_ext.help_chat.help_chat_cog import HelpChatCog
from commanderbot_lib.utils import add_configured_cog
from discord.ext.commands import Bot


def setup(bot: Bot):
    add_configured_cog(bot, HelpChatCog)
