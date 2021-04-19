from discord.ext import commands

from commanderbot_ext.ext.quote.quote_cog import QuoteCog


def setup(bot: commands.Bot):
    bot.add_cog(QuoteCog(bot))
