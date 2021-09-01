from discord.ext.commands import Bot

from commanderbot.ext.faq.faq_cog import FaqCog
from commanderbot.core.utils import add_configured_cog


def setup(bot: Bot):
    add_configured_cog(bot, __name__, FaqCog)
