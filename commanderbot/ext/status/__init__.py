from discord.ext.commands import Bot

from commanderbot.ext.status.status_cog import StatusCog


def setup(bot: Bot):
    bot.add_cog(StatusCog(bot))
