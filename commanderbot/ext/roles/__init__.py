from discord.ext.commands import Bot

from commanderbot.ext.roles.roles_cog import RolesCog
from commanderbot.core.utils import add_configured_cog


def setup(bot: Bot):
    add_configured_cog(bot, __name__, RolesCog)
