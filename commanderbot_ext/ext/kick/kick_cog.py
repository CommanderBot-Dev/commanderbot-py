import logging
from typing import Optional

from discord import Member
from discord.ext.commands import Bot, Cog, Context, command, has_permissions

from commanderbot_ext.lib import checks

LOG = logging.getLogger(__name__)


class KickCog(Cog, name="commanderbot_ext.ext.kick"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @command(name="kick")
    @checks.guild_only()
    @has_permissions(kick_members=True)
    async def cmd_kick(
        self,
        ctx: Context,
        user: Member,
        *,
        reason: Optional[str] = None,
    ):
        # make sure we aren't trying to kick the bot itself
        if user == self.bot.user:
            await ctx.reply("I don't think you want to do that...")
            LOG.warning("Tried to kick the bot itself")
            return

        # attempt to DM if a reason was included
        # we do this before kicking in case this is the only mutual server
        if reason:
            try:
                await user.send(
                    content=f"You were kicked from **{ctx.guild}** for:\n>>> {reason}",
                )
                await ctx.message.add_reaction("✉️")
            except:
                LOG.exception(f"Failed to DM {user} about being kicked")
            else:
                LOG.info(f"Successfully DM'd {user} about being kicked")

        # actually kick the user
        try:
            await user.kick(reason=reason)
            await ctx.message.add_reaction("👢")
        except:
            LOG.exception(f"Failed to kick {user}")
        else:
            LOG.info(f"Successfully kicked {user}")
