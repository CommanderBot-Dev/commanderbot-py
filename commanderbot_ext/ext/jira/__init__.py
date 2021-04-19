from discord.ext import commands

from commanderbot_ext.ext.jira.jira_cog import JiraCog


def setup(bot: commands.Bot):
    bot.add_cog(JiraCog(bot))
