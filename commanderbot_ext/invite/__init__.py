from commanderbot_lib.utils import add_configured_cog
from discord.ext.commands import Bot

from commanderbot_ext.invite.invite_cog import InviteCog


def setup(bot: Bot):
    add_configured_cog(bot, InviteCog)
