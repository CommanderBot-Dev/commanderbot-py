from discord.ext.commands import Bot

from commanderbot.ext.quote.quote_cog import QuoteCog


async def setup(bot: Bot):
    await bot.add_cog(QuoteCog(bot))
