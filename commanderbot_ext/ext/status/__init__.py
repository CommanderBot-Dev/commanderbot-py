from discord.ext import commands

from commanderbot_ext.ext.status.status_cog import StatusCog


def setup(bot: commands.Bot):
    bot.add_cog(StatusCog(bot))
