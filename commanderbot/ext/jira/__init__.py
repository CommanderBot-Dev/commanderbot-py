from discord.ext.commands import Bot

from commanderbot.ext.jira.jira_cog import JiraCog


def setup(bot: Bot):
    bot.add_cog(JiraCog(bot))
