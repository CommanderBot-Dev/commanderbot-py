from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command

from commanderbot.ext.status.status_details import StatusDetails


class StatusCog(Cog, name="commanderbot.ext.status"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @command(name="status")
    async def cmd_status(self, ctx: Context):
        status_details = StatusDetails(self.bot)

        status_embed: Embed = Embed(color=0x00ACED)
        for k, v in status_details.rows.items():
            status_embed.add_field(name=f"{k}", value=f"{v}")

        await ctx.send(embed=status_embed)
