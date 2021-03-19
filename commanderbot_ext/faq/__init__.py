from commanderbot_lib.utils import add_configured_cog
from discord.ext.commands import Bot

from commanderbot_ext.faq.faq_cog import FaqCog


def setup(bot: Bot):
    add_configured_cog(bot, FaqCog)
