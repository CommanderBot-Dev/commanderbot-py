from discord.ext.commands import Bot

from commanderbot.ext.kick.kick_cog import KickCog


async def setup(bot: Bot):
    await bot.add_cog(KickCog(bot))
