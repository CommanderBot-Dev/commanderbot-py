from discord.ext.commands import Bot

from commanderbot.core.utils import add_configured_cog
from commanderbot.ext.manifest.manifest_cog import ManifestCog


def setup(bot: Bot):
    add_configured_cog(bot, __name__, ManifestCog)
