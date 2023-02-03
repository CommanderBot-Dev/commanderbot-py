from typing import Optional

from discord import Interaction, InteractionMessage, Member, Permissions
from discord.app_commands import command, default_permissions, describe, guild_only
from discord.app_commands.checks import bot_has_permissions
from discord.ext.commands import Bot, Cog

from commanderbot.lib.allowed_mentions import AllowedMentions


class KickCog(Cog, name="commanderbot.ext.kick"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @command(name="kick", description="Kick a user from this server")
    @describe(
        user="The user to kick",
        reason="The reason for the kick (This will also be sent as a DM to the user)",
    )
    @guild_only()
    @default_permissions(kick_members=True)
    @bot_has_permissions(kick_members=True)
    async def cmd_kick(
        self, interaction: Interaction, user: Member, reason: Optional[str]
    ):
        # Make sure we aren't trying to kick the bot or the user running the command
        if user == self.bot.user or user == interaction.user:
            await interaction.response.send_message(
                "😳 I don't think you want to do that...", ephemeral=True
            )
            return

        # Make sure we aren't trying to kick users with elevated permissions
        if user.guild_permissions & Permissions.elevated():
            await interaction.response.send_message(
                "😠 You can't kick users with elevated permissions", ephemeral=True
            )
            return

        # Send the kick response and retrieve it so we can reference it later
        kick_msg: str = f"Kicked {user.mention}"
        kick_reason_msg: str = f"for:\n> {reason}"
        await interaction.response.send_message(
            f"{kick_msg} {kick_reason_msg}" if reason else kick_msg,
            allowed_mentions=AllowedMentions.none(),
        )
        response: InteractionMessage = await interaction.original_response()

        # Attempt to DM if a reason was included
        # We do this before kicking in case this is the only mutual server
        if reason:
            try:
                await user.send(
                    content=f"You were kicked from **{interaction.guild}** for:\n> {reason}",
                )
                await response.add_reaction("✉️")
            except:
                pass

        # Actually kick the user
        try:
            await user.kick(reason=reason if reason else "None provided")
            await response.add_reaction("👢")
        except:
            await response.add_reaction("🔥")
