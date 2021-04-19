from discord.ext import commands

from commanderbot_ext.ext.poster_board.poster_board_cog import PosterBoardCog


def setup(bot: commands.Bot):
    bot.add_cog(PosterBoardCog(bot))
