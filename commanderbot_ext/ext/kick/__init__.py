from discord.ext import commands

from commanderbot_ext.ext.kick.kick_cog import KickCog


def setup(bot: commands.Bot):
    bot.add_cog(KickCog(bot))
