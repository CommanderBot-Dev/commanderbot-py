from discord.ext.commands import Bot

from commanderbot.ext.pack.pack_cog import PackCog
from commanderbot.core.utils import add_configured_cog


def setup(bot: Bot):
    add_configured_cog(bot, __name__, PackCog)
