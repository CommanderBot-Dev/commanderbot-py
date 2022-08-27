from discord.ext.commands import Bot

from commanderbot.ext.help_chat.help_chat_cog import HelpChatCog
from commanderbot.core.utils import add_configured_cog


async def setup(bot: Bot):
    await add_configured_cog(bot, __name__, HelpChatCog)
