import sys
from datetime import datetime, timedelta
from logging import Logger, getLogger
from typing import Any, Dict, List, Optional

from discord.ext.commands import Context

from commanderbot.core.commander_bot_base import CommanderBotBase
from commanderbot.core.configured_extension import ConfiguredExtension
from commanderbot.core.error_handling import (
    CommandErrorHandler,
    ErrorHandling,
    EventErrorHandler,
)
from commanderbot.lib import AllowedMentions, EventData, Intents


class CommanderBot(CommanderBotBase):
    def __init__(self, *args, **kwargs):
        # Account for options that don't belong to the discord.py Bot base.
        extensions_data = kwargs.pop("extensions", None)

        # Account for options that need further processing.
        intents = Intents.from_field_optional(kwargs, "intents")
        allowed_mentions = AllowedMentions.from_field_optional(
            kwargs, "allowed_mentions"
        )
        kwargs.update(
            intents=intents or Intents.default(),
            allowed_mentions=allowed_mentions or AllowedMentions.not_everyone(),
        )

        # Initialize discord.py Bot base.
        super().__init__(*args, **kwargs)

        # Grab our own logger instance.
        self.log: Logger = getLogger("CommanderBot")

        # Remember when we started and the last time we connected.
        self._started_at: datetime = datetime.utcnow()
        self._connected_since: Optional[datetime] = None

        # Create an error handling component.
        self.error_handling = ErrorHandling(log=self.log)

        # Warn about a lack of configured intents.
        if intents is None:
            self.log.warning(
                f"No intents configured; using default flags: {self.intents.value}"
            )
        else:
            self.log.info(f"Using intents flags: {self.intents.value}")

        # Configure extensions.
        self.configured_extensions: Dict[str, ConfiguredExtension] = {}
        if extensions_data:
            self._configure_extensions(extensions_data)
        else:
            self.log.warning("No extensions configured.")

    def _configure_extensions(self, extensions_data: list):
        if not isinstance(extensions_data, list):
            raise ValueError(f"Invalid extensions: {extensions_data}")

        self.log.info(f"Processing {len(extensions_data)} extensions...")

        all_extensions: List[ConfiguredExtension] = [
            ConfiguredExtension.from_data(entry) for entry in extensions_data
        ]

        self.configured_extensions = {}
        for ext in all_extensions:
            self.configured_extensions[ext.name] = ext

        enabled_extensions: List[ConfiguredExtension] = [
            ext for ext in all_extensions if not ext.disabled
        ]

        self.log.info(f"Loading {len(enabled_extensions)} enabled extensions...")

        for ext in enabled_extensions:
            self.log.info(f"[->] {ext.name}")
            try:
                self.load_extension(ext.name)
            except:
                self.log.exception(f"Failed to load extension: {ext.name}")

        self.log.info(f"Finished loading extensions.")

    # @implements CommanderBotBase
    @property
    def started_at(self) -> datetime:
        return self._started_at

    # @implements CommanderBotBase
    @property
    def connected_since(self) -> Optional[datetime]:
        return self._connected_since

    # @implements CommanderBotBase
    @property
    def uptime(self) -> Optional[timedelta]:
        if self.connected_since is not None:
            return datetime.utcnow() - self.connected_since

    # @implements CommanderBotBase
    def get_extension_options(self, ext_name: str) -> Optional[Dict[str, Any]]:
        if configured_extension := self.configured_extensions.get(ext_name):
            return configured_extension.options

    # @implements CommanderBotBase
    def add_event_error_handler(self, handler: EventErrorHandler):
        self.error_handling.add_event_error_handler(handler)

    # @implements CommanderBotBase
    def add_command_error_handler(self, handler: CommandErrorHandler):
        self.error_handling.add_command_error_handler(handler)

    # @overrides Bot
    async def on_connect(self):
        self.log.warning("Connected to Discord.")
        self._connected_since = datetime.utcnow()

    # @overrides Bot
    async def on_disconnect(self):
        self.log.warning("Disconnected from Discord.")

    # @overrides Bot
    async def on_error(self, event_method: str, *args: Any, **kwargs: Any):
        _, ex, _ = sys.exc_info()
        if isinstance(ex, Exception):
            event_data = EventData(event_method, args, kwargs)
            await self.error_handling.on_event_error(ex, event_data)
        else:
            await super().on_error(event_method, *args, **kwargs)

    # @overrides Bot
    async def on_command_error(self, ctx: Context, ex: Exception):
        await self.error_handling.on_command_error(ex, ctx)
