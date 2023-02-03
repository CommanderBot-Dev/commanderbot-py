from dataclasses import dataclass
from typing import Optional, Union

from discord import Interaction, TextChannel, Thread

from commanderbot.ext.stacktracer.stacktracer_exceptions import (
    GuildLoggingNotConfigured,
)
from commanderbot.ext.stacktracer.stacktracer_store import StacktracerStore
from commanderbot.lib import CogGuildState, Color, LogOptions


@dataclass
class StacktracerGuildState(CogGuildState):
    """
    Encapsulates the state and logic of the Stacktracer cog, at the guild level.

    Attributes
    -----------
    store
        The store used to interface with persistent data in a database-agnostic way.
    """

    store: StacktracerStore

    async def show_guild_log_options(self, interaction: Interaction):
        log_options = await self.store.get_guild_log_options(self.guild)
        if log_options:
            await interaction.response.send_message(
                f"Error logging is configured for this guild: {log_options.format_channel_name(self.bot)}\n"
                + log_options.format_settings()
            )
        else:
            raise GuildLoggingNotConfigured

    async def set_guild_log_options(
        self,
        interaction: Interaction,
        channel: Union[TextChannel, Thread],
        stacktrace: Optional[bool],
        emoji: Optional[str],
        color: Optional[Color],
    ):
        new_log_options = LogOptions(
            channel=channel.id,
            stacktrace=stacktrace,
            emoji=emoji,
            color=color,
        )
        old_log_options = await self.store.set_guild_log_options(
            self.guild, new_log_options
        )
        if old_log_options:
            await interaction.response.send_message(
                f"Updated the error logging configuration for this guild from: {old_log_options.format_channel_name(self.bot)}\n"
                + f"{old_log_options.format_settings()}\n"
                + f"to: {new_log_options.format_channel_name(self.bot)}\n"
                + new_log_options.format_settings()
            )
        else:
            await interaction.response.send_message(
                f"Set the error logging configuration for this guild: {new_log_options.format_channel_name(self.bot)}\n"
                + new_log_options.format_settings()
            )

    async def remove_guild_log_options(self, interaction: Interaction):
        old_log_options = await self.store.set_guild_log_options(self.guild, None)
        if old_log_options:
            await interaction.response.send_message(
                f"Removed the error logging configuration for this guild: {old_log_options.format_channel_name(self.bot)}\n"
                + old_log_options.format_settings()
            )
        else:
            raise GuildLoggingNotConfigured
