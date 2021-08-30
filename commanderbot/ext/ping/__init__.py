from discord.ext.commands import Bot

from commanderbot.ext.ping.ping_cog import PingCog


def setup(bot: Bot):
    bot.add_cog(PingCog(bot))
