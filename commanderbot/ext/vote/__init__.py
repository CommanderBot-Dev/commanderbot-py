from discord.ext.commands import Bot

from commanderbot.ext.vote.vote_cog import VoteCog


async def setup(bot: Bot):
    await bot.add_cog(VoteCog(bot))
