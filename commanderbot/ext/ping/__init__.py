from discord.ext.commands import Bot

from commanderbot_ext.ext.ping.ping_cog import PingCog


def setup(bot: Bot):
    bot.add_cog(PingCog(bot))
