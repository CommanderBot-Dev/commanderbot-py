from discord.ext.commands import Bot

from commanderbot.core.utils import add_configured_cog
from commanderbot.ext.stacktracer.stacktracer_cog import StacktracerCog


def setup(bot: Bot):
    add_configured_cog(bot, __name__, StacktracerCog)
