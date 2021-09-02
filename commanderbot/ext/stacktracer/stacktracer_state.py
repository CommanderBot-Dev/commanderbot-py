from dataclasses import dataclass
from typing import Optional

from discord import Color, TextChannel, Thread
from discord.ext.commands import Context

from commanderbot.ext.stacktracer.stacktracer_guild_state import StacktracerGuildState
from commanderbot.ext.stacktracer.stacktracer_store import StacktracerStore
from commanderbot.lib import (
    AllowedMentions,
    EventData,
    GuildPartitionedCogState,
    LogOptions,
)
from commanderbot.lib.utils import format_command_context


@dataclass
class StacktracerState(GuildPartitionedCogState[StacktracerGuildState]):
    """
    Encapsulates the state and logic of the stacktracer cog, for each guild.
    """

    store: StacktracerStore

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
                lines = [
                    "Encountered an unhandled event error:",
                    log_options.formate_error_codeblock(error),
                    "Caused by the following event:",
                    event_data.format_codeblock(),
                ]
                content = "\n".join(lines)
                await log_options.send(self.bot, content)
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
                lines = [
                    "Encountered an unhandled command error:",
                    log_options.formate_error_codeblock(error),
                    f"Caused by " + format_command_context(ctx),
                ]
                content = "\n".join(lines)
                await log_options.send(self.bot, content)
                # Stop the error from being printed to console.
                return True
            except:
                # If something went wrong here, print another exception to the console.
                self.log.exception(
                    f"Failed to log command error to channel with ID {log_options.channel}"
                )

    async def reply(self, ctx: Context, content: str):
        """Wraps `Context.reply()` with some extension-default boilerplate."""
        await ctx.message.reply(
            content,
            allowed_mentions=AllowedMentions.none(),
        )

    async def show_global_log_options(self, ctx: Context):
        log_options = await self.store.get_global_log_options()
        if log_options:
            await self.reply(
                ctx,
                f"Global error logging is configured: " + log_options.format(self.bot),
            )
        else:
            await self.reply(ctx, f"Global error logging is not configured.")

    async def set_global_log_options(
        self,
        ctx: Context,
        channel: TextChannel | Thread,
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
            await self.reply(
                ctx,
                "Updated the global error logging configuration from: "
                + old_log_options.format(self.bot)
                + f"\nto: "
                + new_log_options.format(self.bot),
            )
        else:
            await self.reply(
                ctx,
                "Set the global error logging configuration: "
                + new_log_options.format(self.bot),
            )

    async def remove_global_log_options(self, ctx: Context):
        old_log_options = await self.store.set_global_log_options(None)
        if old_log_options:
            await self.reply(
                ctx,
                f"Removed the global error logging configuration: "
                + old_log_options.format(self.bot),
            )
        else:
            await self.reply(ctx, f"Global error logging is not configured.")
