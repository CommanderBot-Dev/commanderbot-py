from discord.ext.commands import Bot

from commanderbot.ext.kick.kick_cog import KickCog


def setup(bot: Bot):
    bot.add_cog(KickCog(bot))
