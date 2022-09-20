from typing import Optional

from discord import Interaction, AllowedMentions

__all__ = ("send_or_followup", "command_name")


async def send_or_followup(
    interaction: Interaction,
    content,
    *,
    allowed_mentions: Optional[AllowedMentions] = None,
    ephemeral=True
):
    """
    Respond to an interaction using `Interaction.response.send_message()`.
    If that has already happened, it sends a followup message using `Interaction.interaction.followup.send` instead.
    """
    mentions: AllowedMentions = allowed_mentions or AllowedMentions.none()
    if not interaction.response.is_done():
        await interaction.response.send_message(
            content,
            allowed_mentions=mentions,
            ephemeral=ephemeral,
        )
    else:
        await interaction.followup.send(
            content,
            allowed_mentions=mentions,
            ephemeral=ephemeral,
        )


def command_name(interaction: Interaction) -> Optional[str]:
    """
    Returns the fully qualified command name.
    """
    return interaction.command.qualified_name if interaction.command else None
