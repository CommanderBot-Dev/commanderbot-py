from discord.ext.commands import Bot

from commanderbot.ext.automod.automod_cog import AutomodCog
from commanderbot.core.utils import add_configured_cog


async def setup(bot: Bot):
    await add_configured_cog(bot, __name__, AutomodCog)
