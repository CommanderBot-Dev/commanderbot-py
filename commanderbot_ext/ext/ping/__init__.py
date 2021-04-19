from discord.ext import commands

from commanderbot_ext.ext.ping.ping_cog import PingCog


def setup(bot: commands.Bot):
    bot.add_cog(PingCog(bot))
