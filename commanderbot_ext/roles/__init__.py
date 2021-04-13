from commanderbot_lib.utils import add_configured_cog
from discord.ext.commands import Bot

from commanderbot_ext.roles.roles_cog import RolesCog


def setup(bot: Bot):
    add_configured_cog(bot, RolesCog)
