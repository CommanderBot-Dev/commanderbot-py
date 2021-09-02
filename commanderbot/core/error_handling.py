from dataclasses import dataclass, field
from logging import Logger
from typing import List, Optional

import discord
from discord.ext.commands import Context
from discord.ext.commands.errors import (
    BotMissingPermissions,
    CheckFailure,
    CommandInvokeError,
    CommandNotFound,
    MissingPermissions,
    NoPrivateMessage,
    UserInputError,
)

from commanderbot.core.commander_bot_base import CommandErrorHandler, EventErrorHandler
from commanderbot.lib import AllowedMentions, EventData, ResponsiveException


@dataclass
class ErrorHandling:
    log: Logger

    event_error_handlers: List[EventErrorHandler] = field(default_factory=list)
    command_error_handlers: List[CommandErrorHandler] = field(default_factory=list)

    def _get_root_error(self, error: Exception) -> Exception:
        if isinstance(error, CommandInvokeError):
            return error.original
        else:
            return error

    def add_event_error_handler(self, handler: EventErrorHandler):
        self.event_error_handlers.append(handler)

    def add_command_error_handler(self, handler: CommandErrorHandler):
        self.command_error_handlers.append(handler)

    async def reply(
        self,
        ctx: Context,
        content: str,
        allowed_mentions: Optional[discord.AllowedMentions] = None,
    ) -> discord.Message:
        """Wraps `Context.reply()` with all mentions disabled by default."""
        return await ctx.message.reply(
            content,
            allowed_mentions=allowed_mentions or AllowedMentions.none(),
        )

    async def on_event_error(self, ex: Exception, event_data: EventData):
        # Extract the root error.
        error = self._get_root_error(ex)

        # Attempt to handle the error ourselves.
        handled = await self.try_handle_event_error(error, event_data)

        # Run the error through our registered event error handlers.
        for handler in self.event_error_handlers:
            try:
                if result := await handler(error, event_data, handled):
                    handled = result
            except:
                # If something went wrong here, print another exception to the console.
                self.log.exception("Handler for command errors caused another error:")

        # If it wasn't handled, re-raise so it can be printed to the console.
        if not handled:
            try:
                raise error
            except:
                self.log.exception(
                    f"Ignoring unhandled exception in event `{event_data.name}`"
                )

    async def try_handle_event_error(
        self, error: Exception, event_data: EventData
    ) -> bool:
        # TODO Can we handle certain types of event errors? #enhance
        return False

    async def on_command_error(self, ex: Exception, ctx: Context):
        # Extract the root error.
        error = self._get_root_error(ex)

        # Attempt to handle the error ourselves.
        handled = await self.try_handle_command_error(error, ctx)

        # Pipe the error through our registered command error handlers, regardless of
        # whether the error was handled. Handlers can decide on their own whether to do
        # anything with errors that have already been handled.
        for handler in self.command_error_handlers:
            try:
                if result := await handler(error, ctx, handled):
                    handled = result
            except:
                # If something went wrong here, print another exception to the console.
                self.log.exception("Handler for command errors caused another error:")

        # If it wasn't handled, re-raise so it can be printed to the console, and then
        # let the user know something went wrong.
        if not handled:
            try:
                raise error
            except:
                cog_name = ctx.cog.__cog_name__ if ctx.cog else None
                self.log.exception(
                    f"Ignoring unhandled exception in cog `{cog_name}` from command: `{ctx.command}`"
                )
            await self.reply(ctx, f"🔥 Something went wrong trying to do that.")

    async def try_handle_command_error(self, error: Exception, ctx: Context) -> bool:
        if isinstance(error, CommandNotFound):
            return True
        elif isinstance(error, UserInputError):
            await self.reply(ctx, f"😬 Bad input: {error}")
            await ctx.send_help(ctx.command)
            return True
        elif isinstance(error, MissingPermissions):
            await self.reply(ctx, f"😠 You don't have permission to do that.")
            return True
        elif isinstance(error, BotMissingPermissions):
            await self.reply(ctx, f"😳 I don't have permission to do that.")
            return True
        elif isinstance(error, NoPrivateMessage):
            await self.reply(ctx, f"🤐 You can't do that in a private message.")
            return True
        elif isinstance(error, CheckFailure):
            await self.reply(ctx, f"🤔 You can't do that.")
            return True
        elif isinstance(error, ResponsiveException):
            await error.respond(ctx)
            return True

        return False
