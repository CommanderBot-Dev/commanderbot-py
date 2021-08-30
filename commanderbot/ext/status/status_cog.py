from discord.ext.commands import Bot, Cog, Context, command

from commanderbot_ext.ext.status.status_details import StatusDetails


class StatusCog(Cog, name="commanderbot_ext.ext.status"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @command(name="status")
    async def cmd_status(self, ctx: Context):
        status_details = StatusDetails(self.bot)
        text = "\n".join(("```", "\n".join(status_details.lines), "```"))
        await ctx.send(text)
