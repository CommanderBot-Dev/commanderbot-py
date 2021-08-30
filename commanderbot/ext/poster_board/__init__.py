from discord.ext.commands import Bot

from commanderbot.ext.poster_board.poster_board_cog import PosterBoardCog


def setup(bot: Bot):
    bot.add_cog(PosterBoardCog(bot))
