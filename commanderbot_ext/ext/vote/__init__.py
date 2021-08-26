from discord.ext.commands import Bot

from commanderbot_ext.ext.vote.vote_cog import VoteCog


def setup(bot: Bot):
    bot.add_cog(VoteCog(bot))
