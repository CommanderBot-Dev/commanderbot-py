from discord.ext.commands import Bot

from commanderbot.ext.manifest.manifest_cog import ManifestCog


def setup(bot: Bot):
    bot.add_cog(ManifestCog(bot))
