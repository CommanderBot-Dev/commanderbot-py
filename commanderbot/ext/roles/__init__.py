from discord.ext.commands import Bot

from commanderbot_ext.ext.roles.roles_cog import RolesCog
from commanderbot_ext.lib.utils import add_configured_cog


def setup(bot: Bot):
    add_configured_cog(bot, __name__, RolesCog)
