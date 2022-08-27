from discord.ext.commands import Bot

from commanderbot.core.utils import add_configured_cog
from commanderbot.ext.jira.jira_cog import JiraCog


async def setup(bot: Bot):
    await add_configured_cog(bot, __name__, JiraCog)
