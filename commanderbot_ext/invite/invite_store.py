from datetime import datetime
from typing import Iterable, Optional

from commanderbot_lib.database.abc.versioned_file_database import (
    DataMigration,
    VersionedFileDatabase,
)
from commanderbot_lib.store.abc.versioned_cached_store import VersionedCachedStore
from discord import Guild, Message

from commanderbot_ext.invite import invite_migrations as migrations
from commanderbot_ext.invite.invite_cache import InviteCache, InviteEntry, InviteGuildData
from commanderbot_ext.invite.invite_options import InviteOptions


class InviteStore(VersionedCachedStore[InviteOptions, VersionedFileDatabase, InviteCache]):
    # @implements CachedStore
    async def _build_cache(self, data: dict) -> InviteCache:
        return await InviteCache.deserialize(data)

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
        if actual_version < 1:
            yield migrations.m_1a_init_aliases_dates_hits

    # @implements VersionedCachedStore
    @property
    def data_version(self) -> int:
        return 1

    def get_guild_data(self, guild: Guild) -> Optional[InviteGuildData]:
        return self._cache.guilds.get(guild.id)

    async def iter_guild_Invites(self, guild: Guild) -> Optional[Iterable[InviteEntry]]:
        if guild_data := self.get_guild_data(guild):
            return guild_data.entries.values()

    async def get_guild_Invite_by_name(
        self, guild: Guild, Invite_name: str
    ) -> Optional[InviteEntry]:
        if guild_data := self.get_guild_data(guild):
            return guild_data.entries.get(Invite_name)
