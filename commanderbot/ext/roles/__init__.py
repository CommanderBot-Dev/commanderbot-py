from discord.ext.commands import Bot

from commanderbot.ext.roles.roles_cog import RolesCog
from commanderbot.core.utils import add_configured_cog


async def setup(bot: Bot):
    await add_configured_cog(bot, __name__, RolesCog)
