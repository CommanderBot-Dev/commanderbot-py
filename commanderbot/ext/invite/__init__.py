from discord.ext.commands import Bot

from commanderbot.ext.invite.invite_cog import InviteCog
from commanderbot.core.utils import add_configured_cog


def setup(bot: Bot):
    add_configured_cog(bot, __name__, InviteCog)
