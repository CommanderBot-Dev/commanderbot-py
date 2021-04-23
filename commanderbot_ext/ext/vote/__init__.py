from discord.ext import commands

from commanderbot_ext.ext.vote.vote_cog import VoteCog


def setup(bot: commands.Bot):
    bot.add_cog(VoteCog(bot))
