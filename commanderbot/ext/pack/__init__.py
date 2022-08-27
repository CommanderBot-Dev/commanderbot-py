from discord.ext.commands import Bot

from commanderbot.ext.pack.pack_cog import PackCog
from commanderbot.core.utils import add_configured_cog


async def setup(bot: Bot):
    await add_configured_cog(bot, __name__, PackCog)
