from discord.ext.commands import Bot

from commanderbot.ext.allay.allay_cog import AllayCog


def setup(bot: Bot):
    bot.add_cog(AllayCog(bot))
