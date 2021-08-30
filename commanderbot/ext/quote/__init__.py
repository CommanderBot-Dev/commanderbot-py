from discord.ext.commands import Bot

from commanderbot_ext.ext.quote.quote_cog import QuoteCog


def setup(bot: Bot):
    bot.add_cog(QuoteCog(bot))
