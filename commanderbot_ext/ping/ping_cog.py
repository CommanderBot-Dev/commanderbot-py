from discord.ext.commands import Bot, Cog, Context, command


class PingCog(Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @command(name="ping")
    async def cmd_ping(self, ctx: Context):
        await ctx.send(f"Pong! Latency: {round(self.bot.latency, 2)}s")
