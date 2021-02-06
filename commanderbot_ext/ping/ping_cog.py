import discord
from commanderbot_lib.logging import Logger, get_clogger
from discord.ext.commands import Bot, Cog, Context, command


class PingCog(Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self._log: Logger = get_clogger(self)

    @command(name="ping")
    async def cmd_ping(self, ctx: discord.Message):
        await ctx.send(f"Pong! Latency: {round(self.bot.latency, 2)}ms")
