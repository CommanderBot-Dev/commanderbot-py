from discord.ext.commands import Bot

from commanderbot.ext.ping.ping_cog import PingCog


async def setup(bot: Bot):
    await bot.add_cog(PingCog(bot))
