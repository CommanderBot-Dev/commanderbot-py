from discord.ext.commands import Bot, Cog, Context, command


class PingCog(Cog, name="commanderbot_ext.ext.ping"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @command(name="ping")
    async def cmd_ping(self, ctx: Context):
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! Latency: {latency_ms}ms")
