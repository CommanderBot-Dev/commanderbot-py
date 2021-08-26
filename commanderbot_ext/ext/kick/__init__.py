from discord.ext.commands import Bot

from commanderbot_ext.ext.kick.kick_cog import KickCog


def setup(bot: Bot):
    bot.add_cog(KickCog(bot))
