from discord.ext.commands import Bot

from commanderbot.ext.poster_board.poster_board_cog import PosterBoardCog


async def setup(bot: Bot):
    await bot.add_cog(PosterBoardCog(bot))
