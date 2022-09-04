from discord.ext.commands import Bot

from commanderbot.ext.sudo.sudo_cog import SudoCog


async def setup(bot: Bot):
    await bot.add_cog(SudoCog(bot))
