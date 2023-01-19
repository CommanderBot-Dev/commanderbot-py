from collections import defaultdict
from dataclasses import dataclass, field
from logging import Logger, getLogger
from typing import DefaultDict, Dict, Iterable, List, Optional, TypeAlias, Union

from discord import AppCommandType
from discord.abc import Snowflake
from discord.app_commands import AppCommand, AppCommandGroup, Argument, CommandTree

from commanderbot.lib import AppCommandID, GuildID

__all__ = ("CachingCommandTree",)

Cache: TypeAlias = Dict[str, AppCommand]
GuildType: TypeAlias = Union[Snowflake, GuildID]


@dataclass
class CommandCache:
    """
    Abstracts the command cache and adds helpful functions for searching or modifying it
    """

    _cache: Cache = field(default_factory=dict)

    def find(self, command: Union[str, AppCommandID]) -> Optional[AppCommand]:
        """
        Searches the cache for a command or group that matches `command`
        """
        for name, cmd in self._cache.items():
            # Try to match commands or groups by name
            if name == command:
                return cmd

            # Try to match commands by their ID
            if isinstance(cmd, AppCommand) and str(command).isdigit():
                if cmd.id == int(command):
                    return cmd

    def update(self, commands: List[AppCommand], *, override: bool = True):
        """
        Updates the cache using the commands passed to `commands`.
        Also has an option to override the cache if necessary.
        """

        # Traverse the options tree and all groups it visits
        def traverse_options(options: List[Union[AppCommandGroup, Argument]]):
            for option in options:
                if isinstance(option, AppCommandGroup):
                    self._cache[option.qualified_name] = option  # type: ignore
                    traverse_options(option.options)

        # Add commands and their options
        if override:
            self.clear()
        for command in commands:
            self._cache[command.name] = command
            if command.options:
                traverse_options(command.options)

    def clear(self):
        self._cache.clear()

    @property
    def commands(self) -> list[AppCommand]:
        return list(self._cache.values())


class CachingCommandTree(CommandTree):
    """
    A subclass of `CommandTree` that adds an app command caching feature

    Since Discord.py doesn't have a way to retrieve app commands without doing
    an API call, we need to cache them to minimize API calls

    To initialize the cache, bots should call `build_cache()`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log: Logger = getLogger("CachingCommandTree")
        self._global_cache: CommandCache = CommandCache()
        self._guild_cache: DefaultDict[GuildID, CommandCache] = defaultdict(
            CommandCache
        )

    def _get_cache(
        self, *, guild: Optional[GuildType] = None
    ) -> Optional[CommandCache]:
        if guild:
            return self._guild_cache.get(self._guild_to_id(guild))
        else:
            self._global_cache

    def _guild_to_id(self, guild: GuildType) -> GuildID:
        return guild.id if isinstance(guild, Snowflake) else guild

    def get_app_command(
        self, command: Union[str, AppCommandID], *, guild: Optional[GuildType] = None
    ) -> Optional[AppCommand]:
        # Return early if we're searching the global cache
        if not guild:
            return self._global_cache.find(command)

        # Try to find the command in the guild cache
        if cache := self._get_cache(guild=guild):
            if self.fallback_to_global:
                return cache.find(command) or self._global_cache.find(command)
            else:
                return cache.find(command)

    def update_cache(
        self,
        commands: List[AppCommand],
        *,
        guild: Optional[GuildType] = None,
        override: bool = True,
    ):
        if guild:
            guild_id: GuildID = self._guild_to_id(guild)
            self._guild_cache[guild_id].update(commands, override=override)
        else:
            self._global_cache.update(commands, override=override)

    def clear_cache(self, *, guild: Optional[GuildType] = None):
        if guild:
            guild_id: GuildID = self._guild_to_id(guild)
            self._guild_cache.pop(guild_id, None)
        else:
            self._global_cache.clear()

    async def build_cache(self, *, guilds: Optional[Iterable[Snowflake]]):
        """
        Builds the command cache using app commands that are currently synced to Discord
        """
        self._log.info(
            "Building command cache from the currently synced app commands..."
        )

        await self.fetch_commands(use_cache=False)
        for guild in guilds if guilds else []:
            await self.fetch_commands(guild=guild, use_cache=False)

        self._log.info("Done building command cache.")

    # @overrides CommandTree
    async def fetch_command(
        self,
        command_id: int,
        /,
        *,
        guild: Optional[Snowflake] = None,
        use_cache: bool = True,
    ) -> AppCommand:
        # Try searching the cache first
        if use_cache and (cache := self._get_cache(guild=guild)):
            if cmd := cache.find(command_id):
                return cmd

        # If the cache/command wasn't found or we don't want to use the cache,
        # try getting the command from the API
        command = await super().fetch_command(command_id, guild=guild)
        self.update_cache([command], guild=guild, override=False)
        return command

    # @overrides CommandTree
    async def fetch_commands(
        self, *, guild: Optional[Snowflake] = None, use_cache: bool = True
    ) -> List[AppCommand]:
        # Try searching the cache first
        if use_cache and (cache := self._get_cache(guild=guild)):
            return cache.commands

        # If the cache/commands weren't found or we don't want to use the cache,
        # try getting the commands from the API
        commands = await super().fetch_commands(guild=guild)
        self.update_cache(commands, guild=guild)
        return commands

    # @overrides CommandTree
    async def sync(self, *, guild: Optional[Snowflake] = None) -> List[AppCommand]:
        # Create log messages
        sync_msg: str = "global app commands"
        cache_msg: str = "global command cache"
        if guild:
            sync_msg = f"app commands to guild {guild.id}"
            cache_msg = f"command cache for guild {guild.id}"

        # Sync commands
        try:
            self._log.info(f"Started syncing {sync_msg}...")
            commands = await super().sync(guild=guild)
            self._log.info(f"Finished syncing {len(commands)} {sync_msg}.")
        except Exception as ex:
            self._log.warn(f"Unable to sync {sync_msg}. Reason: {ex}")
            raise ex

        # Update cache
        self._log.info(f"Started updating {cache_msg}...")
        self.update_cache(commands, guild=guild)
        self._log.info(f"Finished updating {cache_msg}.")

        return commands

    # @overrides CommandTree
    def clear_commands(
        self,
        *,
        guild: Optional[Snowflake] = None,
        type: Optional[AppCommandType] = None,
        clear_cache: bool = True,
    ):
        super().clear_commands(guild=guild, type=type)
        if clear_cache:
            self.clear_cache(guild=guild)
