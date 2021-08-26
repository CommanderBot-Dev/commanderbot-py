from discord.ext.commands import Bot

from commanderbot_ext.ext.status.status_cog import StatusCog


def setup(bot: Bot):
    bot.add_cog(StatusCog(bot))
