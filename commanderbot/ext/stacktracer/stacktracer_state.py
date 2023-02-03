from dataclasses import dataclass
from typing import Optional, Union

from discord import Interaction, TextChannel, Thread
from discord.ext.commands import Context

from commanderbot.core.utils import get_app_command
from commanderbot.ext.stacktracer.stacktracer_exceptions import LoggingNotConfigured
from commanderbot.ext.stacktracer.stacktracer_guild_state import StacktracerGuildState
from commanderbot.ext.stacktracer.stacktracer_store import StacktracerStore
from commanderbot.lib import Color, EventData, GuildPartitionedCogState, LogOptions
from commanderbot.lib.interactions import command_name
from commanderbot.lib.utils import format_context_cause


@dataclass
class StacktracerState(GuildPartitionedCogState[StacktracerGuildState]):
    """
    Encapsulates the state and logic of the stacktracer cog, for each guild.
    """

    store: StacktracerStore

    def _format_command(self, command: Union[Context, Interaction]) -> str:
        if isinstance(command, Context) and (cmd := command.command):
            return f"`{command.prefix}{cmd}`"
        elif isinstance(command, Interaction):
            if cmd := get_app_command(self.bot, command):
                return cmd.mention
            elif cmd := command_name(command):
                return f"`/{cmd}`"
        return "`Unknown Command`"

    async def handle_event_error(
        self, error: Exception, event_data: EventData, handled: bool
    ) -> Optional[bool]:
        # If the error was already handled, ignore it.
        if handled:
            return

        # TODO Can we detect guild event errors by inspecting event data? #enhance

        # Attempt to print the error to the log channel, if any.
        if log_options := await self.store.get_global_log_options():
            try:
                title = "Encountered an unhandled event error"
                description = "\n".join(
                    [
                        log_options.formate_error_codeblock(error),
                        "Caused by the following event:",
                        event_data.format_codeblock(),
                    ]
                )
                alt_description = (
                    "While handling an event, the attached error occurred:"
                )
                await log_options.send_embed(
                    self.bot,
                    title=title,
                    description=description,
                    file_callback=lambda: (
                        title,
                        alt_description,
                        description,
                        "error.txt",
                    ),
                )
                # Stop the error from being printed to console.
                return True
            except:
                # If something went wrong here, print another exception to the console.
                self.log.exception(
                    f"Failed to log event error to channel with ID {log_options.channel}"
                )

    async def handle_command_error(
        self, error: Exception, ctx: Context, handled: bool
    ) -> Optional[bool]:
        # If the error was already handled, ignore it.
        if handled:
            return

        # If this error originated from a guild, use the guild's logging configuration.
        if guild := ctx.guild:
            log_options = await self.store.get_guild_log_options(guild)
        # Otherwise, use the global logging configuration.
        else:
            log_options = await self.store.get_global_log_options()

        # Attempt to print the error to the log channel, if any.
        if log_options:
            try:
                title = "Encountered an unhandled command error"
                command = self._format_command(ctx)
                cause = format_context_cause(ctx)
                description = "\n".join(
                    [
                        f"While executing {command} for {cause}, the following error occurred:",
                        log_options.formate_error_codeblock(error),
                    ]
                )
                alt_description = f"While executing {command} for {cause}, the attached error occurred:"
                await log_options.send_embed(
                    self.bot,
                    title=title,
                    description=description,
                    file_callback=lambda: (
                        title,
                        alt_description,
                        description,
                        "error.txt",
                    ),
                )
                # Stop the error from being printed to console.
                return True
            except:
                # If something went wrong here, print another exception to the console.
                self.log.exception(
                    f"Failed to log command error to channel with ID {log_options.channel}"
                )

    async def handle_app_command_error(
        self, error: Exception, interaction: Interaction, handled: bool
    ) -> Optional[bool]:
        # If the error was already handled, ignore it.
        if handled:
            return

        # If this error originated from a guild, use the guild's logging configuration.
        if guild := interaction.guild:
            log_options = await self.store.get_guild_log_options(guild)
        # Otherwise, use the global logging configuration.
        else:
            log_options = await self.store.get_global_log_options()

        # Attempt to print the error to the log channel, if any.
        if log_options:
            try:
                title = "Encountered an unhandled app command error"
                command = self._format_command(interaction)
                cause = format_context_cause(interaction)
                description = "\n".join(
                    [
                        f"While executing {command} for {cause}, the following error occurred:",
                        log_options.formate_error_codeblock(error),
                    ]
                )
                alt_description = f"While executing {command} for {cause}, the attached error occurred:"
                await log_options.send_embed(
                    self.bot,
                    title=title,
                    description=description,
                    file_callback=lambda: (
                        title,
                        alt_description,
                        description,
                        "error.txt",
                    ),
                )
                # Stop the error from being printed to console.
                return True
            except:
                # If something went wrong here, print another exception to the console.
                self.log.exception(
                    f"Failed to log app command error to channel with ID {log_options.channel}"
                )

    async def show_global_log_options(self, interaction: Interaction):
        log_options = await self.store.get_global_log_options()
        if log_options:
            await interaction.response.send_message(
                f"Global error logging is configured: {log_options.format_channel_name(self.bot)}\n"
                + log_options.format_settings()
            )
        else:
            raise LoggingNotConfigured

    async def set_global_log_options(
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
        old_log_options = await self.store.set_global_log_options(new_log_options)
        if old_log_options:
            await interaction.response.send_message(
                f"Updated the global error logging configuration from: {old_log_options.format_channel_name(self.bot)}\n"
                + f"{old_log_options.format_settings()}\n"
                + f"to: {new_log_options.format_channel_name(self.bot)}\n"
                + new_log_options.format_settings()
            )
        else:
            await interaction.response.send_message(
                f"Set the global error logging configuration: {new_log_options.format_channel_name(self.bot)}\n"
                + new_log_options.format_settings()
            )

    async def remove_global_log_options(
        self,
        interaction: Interaction,
    ):
        old_log_options = await self.store.set_global_log_options(None)
        if old_log_options:
            await interaction.response.send_message(
                f"Removed the global error logging configuration: {old_log_options.format_channel_name(self.bot)}\n"
                + old_log_options.format_settings()
            )
        else:
            raise LoggingNotConfigured
