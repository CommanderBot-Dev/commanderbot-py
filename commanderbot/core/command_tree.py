from collections import defaultdict
from dataclasses import dataclass, field
from logging import Logger, getLogger
from typing import DefaultDict, Dict, Iterable, List, Optional, TypeAlias, Union

from discord import AppCommandType, Object
from discord.abc import Snowflake
from discord.app_commands import AppCommand, AppCommandGroup, Argument, CommandTree

from commanderbot.lib import AppCommandID, GuildID

__all__ = ("CachingCommandTree",)

CommandOrGroup: TypeAlias = Union[AppCommand, AppCommandGroup]
Cache: TypeAlias = Dict[str, CommandOrGroup]

GuildType: TypeAlias = Union[Snowflake, GuildID]


@dataclass
class CommandCache:
    """
    Abstracts the command cache and adds helpful functions for searching or modifying it
    """

    _cache: Cache = field(default_factory=dict)

    def find(self, command_str: Union[str, AppCommandID]) -> Optional[CommandOrGroup]:
        """
        Searches the cache for a command or group that matches `command_str`
        """

        for name, cmd in self._cache.items():
            # Try to match commands or groups by name
            if name == command_str:
                return cmd

            # If we get this far, we can only check for app commands
            if isinstance(cmd, AppCommand) and str(command_str).isdigit():
                if cmd.id == int(command_str):
                    return cmd

    def update(self, commands: List[AppCommand]):
        """
        Updates the cache using the `commands` list
        """
        cache: Cache = {}

        # Traverse the options tree and all groups it visits
        def traverse_options(options: List[Union[AppCommandGroup, Argument]]):
            for option in options:
                if isinstance(option, AppCommandGroup):
                    cache[option.qualified_name] = option
                    traverse_options(option.options)

        # Add commands and their options
        for command in commands:
            cache[command.name] = command
            if command.options:
                traverse_options(command.options)

        # Update cache
        self._cache = cache

    def clear(self):
        """
        Clears the cache
        """
        self._cache.clear()


class CachingCommandTree(CommandTree):
    """
    A subclass of `CommandTree` that adds an app command caching feature

    Since Discord.py doesn't have a way to retrieve app commands without doing
    an API call, we need to cache them to minimize API calls

    To initialize the cache without needing to manually sync, bots should call `build_cache()`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log: Logger = getLogger("CachingCommandTree")
        self._global_cache: CommandCache = CommandCache()
        self._guild_cache: DefaultDict[GuildID, CommandCache] = defaultdict(
            CommandCache
        )

    def get_app_command(
        self, command: Union[str, AppCommandID], *, guild: Optional[GuildType] = None
    ) -> Optional[AppCommand]:
        """
        Tries to find an app command with the name or ID passed to `command`
        """
        if found_command := self._try_get_command_or_group(command, guild=guild):
            if isinstance(found_command, AppCommand):
                return found_command

    def get_app_command_group(
        self, group: str, *, guild: Optional[GuildType] = None
    ) -> Optional[AppCommandGroup]:
        """
        Tries to find an app command group with the name passed to `group`
        """
        if found_group := self._try_get_command_or_group(group, guild=guild):
            if isinstance(found_group, AppCommandGroup):
                return found_group

    def _try_get_command_or_group(
        self, value: Union[str, AppCommandID], *, guild: Optional[GuildType] = None
    ) -> Optional[CommandOrGroup]:
        # Return early if we're looking for a global command/group
        if not guild:
            return self._global_cache.find(value)

        # Get guild ID
        guild_id: GuildID = guild.id if isinstance(guild, Snowflake) else guild

        # If the guild is in the cache, try to get the command/group from it
        if cache := self._guild_cache.get(guild_id):
            if self.fallback_to_global:
                return cache.find(value) or self._global_cache.find(value)
            else:
                return cache.find(value)

    async def update_cache(
        self,
        commands: Optional[List[AppCommand]] = None,
        *,
        guild: Optional[GuildType] = None,
    ):
        """
        Updates the command cache for global or guild app commands
        """
        # Create guild if it exists
        maybe_guild: Optional[Snowflake] = None
        if guild:
            maybe_guild = guild if isinstance(guild, Snowflake) else Object(id=guild)

        # If we didn't pass any commands to this function, fetch the currently synced commands
        if not commands:
            commands = await super().fetch_commands(guild=maybe_guild)

        # Create cache
        if maybe_guild:
            self._guild_cache[maybe_guild.id].update(commands)
        else:
            self._global_cache.update(commands)

    async def build_cache(self, *, guilds: Optional[Iterable[Snowflake]]):
        """
        Builds the command cache using app commands that are currently synced to Discord
        """
        self._log.info(
            "Building command cache from the currently synced app commands..."
        )

        await self.update_cache()
        if guilds:
            for guild in guilds:
                await self.update_cache(guild=guild)

        self._log.info("Done building command cache.")

    def clear_cache(self, *, guild: Optional[Snowflake] = None):
        """
        Clears the command cache for global or guild app commands
        """
        if guild:
            self._guild_cache.pop(guild.id, None)
        else:
            self._global_cache.clear()

    # @overrides CommandTree
    async def fetch_commands(
        self, *, guild: Optional[Snowflake] = None
    ) -> List[AppCommand]:
        """
        A wrapper around `CommandTree.fetch_commands()` that caches the commands it receives
        """
        commands = await super().fetch_commands(guild=guild)
        await self.update_cache(commands, guild=guild)
        return commands

    # @overrides CommandTree
    def clear_commands(
        self,
        *,
        guild: Optional[Snowflake] = None,
        type: Optional[AppCommandType] = None,
        clear_cache: bool = True,
    ):
        """
        A wrapper around `CommandTree.clear_commands()` with an option to clear the command cache
        """
        super().clear_commands(guild=guild, type=type)
        if clear_cache:
            self.clear_cache(guild=guild)

    # @overrides CommandTree
    async def sync(self, *, guild: Optional[Snowflake] = None) -> List[AppCommand]:
        """
        A wrapper around `CommandTree.sync()` that updates the command cache
        """
        commands = await super().sync(guild=guild)

        # Create log message
        msg: str = "global command cache"
        if guild:
            msg = f"command cache for guild {guild.id}"

        # Update cache
        self._log.info(f"Started updating {msg}...")
        await self.update_cache(commands, guild=guild)
        self._log.info(f"Finished updating {msg}.")

        return commands
