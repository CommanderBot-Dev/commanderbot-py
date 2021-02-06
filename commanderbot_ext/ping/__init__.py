from commanderbot_ext.ping.ping_cog import PingCog
from discord.ext import commands


def setup(bot: commands.Bot):
    bot.add_cog(PingCog(bot))
