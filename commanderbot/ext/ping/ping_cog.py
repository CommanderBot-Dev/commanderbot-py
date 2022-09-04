from discord import app_commands, Interaction
from discord.ext.commands import Bot, Cog


class PingCog(Cog, name="commanderbot.ext.ping"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @app_commands.command(name="ping", description="Ping the bot")
    async def cmd_ping(self, interaction: Interaction):
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latency: `{latency_ms}`ms")
