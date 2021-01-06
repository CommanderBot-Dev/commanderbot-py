from typing import Iterable, Optional

from commanderbot_ext.help_chat.help_chat_cache import HelpChannel, HelpChatCache, HelpChatGuildData
from commanderbot_ext.help_chat.help_chat_options import HelpChatOptions
from commanderbot_lib.database.abc.versioned_file_database import (
    DataMigration,
    VersionedFileDatabase,
)
from commanderbot_lib.store.abc.versioned_cached_store import VersionedCachedStore
from discord import Guild, TextChannel


class HelpChatStore(VersionedCachedStore[HelpChatOptions, VersionedFileDatabase, HelpChatCache]):
    # @implements CachedStore
    async def _build_cache(self, data: dict) -> HelpChatCache:
        return await HelpChatCache.deserialize(data)

    # @implements CachedStore
    async def serialize(self) -> dict:
        return self._cache.serialize()

    # @implements VersionedCachedStore
    def _collect_migrations(
        self,
        database: VersionedFileDatabase,
        actual_version: int,
        expected_version: int,
    ) -> Iterable[DataMigration]:
        # Nothing to do here... yet.
        if False:
            yield

    # @implements VersionedCachedStore
    @property
    def data_version(self) -> int:
        return 1

    def get_guild_data(self, guild: Guild) -> Optional[HelpChatGuildData]:
        return self._cache.guilds.get(guild.id)

    async def get_guild_help_channel(
        self, guild: Guild, channel: TextChannel
    ) -> Optional[HelpChannel]:
        if guild_data := self.get_guild_data(guild):
            for help_channel in guild_data.help_channels:
                if help_channel.channel_id == channel.id:
                    return help_channel

    async def iter_guild_help_channels(self, guild: Guild) -> Optional[Iterable[HelpChannel]]:
        if guild_data := self.get_guild_data(guild):
            return guild_data.help_channels

    async def add_guild_help_channel(self, guild: Guild, help_channel: HelpChannel):
        guild_data = self.get_guild_data(guild)
        if guild_data is None:
            guild_data = HelpChatGuildData(guild_id=guild.id, help_channels=[])
            self._cache.guilds[guild.id] = guild_data
        guild_data.help_channels.append(help_channel)
        await self.dirty()

    async def remove_guild_help_channel(
        self, guild: Guild, help_channel: HelpChannel
    ) -> Optional[HelpChannel]:
        if guild_data := self.get_guild_data(guild):
            guild_data.help_channels.remove(help_channel)
            await self.dirty()
