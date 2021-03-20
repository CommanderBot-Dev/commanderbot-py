from datetime import datetime
from typing import Iterable, Optional

from commanderbot_lib.database.abc.versioned_file_database import (
    DataMigration,
    VersionedFileDatabase,
)
from commanderbot_lib.store.abc.versioned_cached_store import VersionedCachedStore
from discord import Guild, Message

from commanderbot_ext.invite import invite_migrations as migrations
from commanderbot_ext.invite.invite_cache import (
    InviteCache,
    InviteEntry,
    InviteGuildData,
)
from commanderbot_ext.invite.invite_options import InviteOptions

class NotExistException(Exception): pass
class NotApplicableException(Exception): pass

class InviteStore(
    VersionedCachedStore[InviteOptions, VersionedFileDatabase, InviteCache]
):
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

    # Using an improved version of this method that will create the guild data if there is none
    def guild_data(self, guild: Guild) -> InviteGuildData:
        if guild.id not in self._cache.guilds:
            self._cache.add_guild(guild.id)
        return self._cache.guilds[guild.id]

    async def iter_guild_invites(self, guild: Guild) -> Iterable[InviteEntry]:
        return self.guild_data(guild).entries.values()

    async def get_guild_invite_by_name(
        self, guild: Guild, Invite_name: str
    ) -> Optional[InviteEntry]:
        return self.guild_data(guild).entries.get(Invite_name)

    async def add_invite(
        self, guild: Guild, name: str, link: str
    ) -> Optional[InviteEntry]:
        guild_data = self.guild_data(guild)
        if name in guild_data.entries:
            return guild_data.entries[name]
        else:
            guild_data.entries[name] = InviteEntry(name=name, link=link, tags=set())
            await self.dirty()

    async def remove_invite(self, guild: Guild, name: str) -> bool:
        guild_data = self.guild_data(guild)
        if name not in guild_data.entries:
            return False
        del guild_data.entries[name]
        await self.dirty()
        return True

    async def add_tag(self, guild: Guild, name: str, tag: str):
        guild_data = self.guild_data(guild)
        if name not in guild_data.entries:
            raise NotExistException
        if tag in guild_data.entries[name].tags:
            raise NotApplicableException
        guild_data.entries[name].tags.add(tag)
        await self.dirty()

    async def remove_tag(self, guild: Guild, name: str, tag: str):
        guild_data = self.guild_data(guild)
        if name not in guild_data.entries:
            raise NotExistException
        if tag not in guild_data.entries[name].tags:
            raise NotApplicableException
        guild_data.entries[name].tags.remove(tag)
        await self.dirty()