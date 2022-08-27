from discord.ext.commands import Bot

from commanderbot.ext.allay.allay_cog import AllayCog


async def setup(bot: Bot):
    await bot.add_cog(AllayCog(bot))
