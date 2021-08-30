from typing import Optional

from discord import Member
from discord.ext.commands import Bot, Cog, Context, command, has_permissions

from commanderbot.lib import checks


class KickCog(Cog, name="commanderbot.ext.kick"):
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
            await ctx.message.reply("I don't think you want to do that...")
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
                pass

        # actually kick the user
        try:
            await user.kick(reason=reason)
            await ctx.message.add_reaction("👢")
        except:
            await ctx.message.add_reaction("🔥")
