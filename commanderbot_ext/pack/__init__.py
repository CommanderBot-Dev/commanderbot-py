from commanderbot_lib.utils import add_configured_cog
from discord.ext.commands import Bot

from commanderbot_ext.pack.pack_cog import PackCog


def setup(bot: Bot):
    add_configured_cog(bot, PackCog)
