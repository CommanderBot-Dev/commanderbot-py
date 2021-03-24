from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterable, Dict, Iterable, Optional, Tuple

from discord import Guild

from commanderbot_ext._lib.cog_store import CogStore
from commanderbot_ext._lib.json_file_database import JsonFileDatabase
from commanderbot_ext._lib.types import GuildID, GuildRole, RoleID


class RolesSerializer:
    pass


@dataclass
class RolesRoleEntry:
    added_on: datetime
    joinable: bool
    leavable: bool

    @staticmethod
    def deserialize(data: dict) -> "RolesRoleEntry":
        return RolesRoleEntry(
            added_on=datetime.fromisoformat(data["added_on"]),
            joinable=bool(data["joinable"]),
            leavable=bool(data["leavable"]),
        )

    def serialize(self) -> dict:
        return {
            "added_on": self.added_on.isoformat(),
            "joinable": self.joinable,
            "leavable": self.leavable,
        }


@dataclass
class RolesGuildData:
    role_entries: Dict[RoleID, RolesRoleEntry]

    @staticmethod
    def deserialize(data: dict) -> "RolesGuildData":
        return RolesGuildData(
            role_entries={
                int(role_id): RolesRoleEntry.deserialize(raw_role_entry)
                for role_id, raw_role_entry in data["role_entries".items()]
            }
        )

    def serialize(self) -> dict:
        return {
            "role_entries": {
                str(role_id): role_entry.serialize()
                for role_id, role_entry in self.role_entries.items()
            }
        }

    def get_role_entry(self, role: GuildRole) -> Optional[RolesRoleEntry]:
        # Return the corresponding role entry, if any.
        return self.role_entries.get(role.id)

    def add_role(
        self, role: GuildRole, joinable: bool, leavable: bool
    ) -> RolesRoleEntry:
        # Create a new role entry and add it to the map. If the role is already present,
        # just replace it with the new information.
        added_role_entry = RolesRoleEntry(
            added_on=datetime.utcnow(),
            joinable=joinable,
            leavable=leavable,
        )
        self.role_entries[role.id] = added_role_entry
        # Return the newly-added role entry.
        return added_role_entry

    def remove_role(self, role: GuildRole) -> Optional[RolesRoleEntry]:
        # Pop and return the corresponding role entry, if any.
        return self.role_entries.pop(role.id, None)


@dataclass
class RolesCache:
    guilds: Dict[GuildID, RolesGuildData]

    @staticmethod
    def deserialize(data: dict) -> "RolesCache":
        return RolesCache(
            guilds={
                int(guild_id): RolesGuildData.deserialize(raw_guild_data)
                for guild_id, raw_guild_data in data["guilds"].items()
            }
        )

    def serialize(self) -> dict:
        return {
            "guilds": {
                str(guild_id): guild_data.serialize()
                for guild_id, guild_data in self.guilds.items()
            }
        }

    def iter_role_entries(
        self, guild: Guild
    ) -> Iterable[Tuple[RoleID, RolesRoleEntry]]:
        # Get this guild's data, if any.
        if guild_data := self.guilds.get(guild.id):
            # Iterate over each role entry for this guild.
            for role_id, role_entry in guild_data.role_entries.items():
                yield role_id, role_entry

    def get_role_entry(self, role: GuildRole) -> Optional[RolesRoleEntry]:
        # Get this guild's data, if any.
        if guild_data := self.guilds.get(role.guild.id):
            # Return the corresponding role entry, if any.
            return guild_data.get_role_entry(role)

    def add_role(
        self, role: GuildRole, joinable: bool, leavable: bool
    ) -> RolesRoleEntry:
        # Get this guild's data, if any.
        guild_data = self.guilds.get(role.guild.id)
        # If this guild doesn't have data, initialize it.
        if not guild_data:
            guild_data = RolesGuildData({})
            self.guilds[role.guild.id] = guild_data
        # Add and return the role to the guild's role entries.
        return guild_data.add_role(role, joinable, leavable)

    def remove_role(self, role: GuildRole) -> Optional[RolesRoleEntry]:
        # Get this guild's data, if any.
        if guild_data := self.guilds.get(role.guild.id):
            # Remove and return the role from the guild's role entries, if it's there.
            return guild_data.remove_role(role)


@dataclass
class RolesStore(CogStore):
    database: Optional[JsonFileDatabase]

    # Lazily-initialized in-memory representation of state. The
    # reason this is lazy is because it needs to be asynchronously initialized from
    # within an async method. Do not use this member; use `_get_cache()` instead.
    __cache: Optional[RolesCache] = field(init=False)

    async def __init_cache(self):
        # If we have a database, initialize the cache based on that.
        if self.database:
            data = await self.database.read()
            self.__cache = RolesCache.deserialize(data)
        # Otherwise, just create a fresh new empty cache.
        else:
            self.__cache = RolesCache({})

    async def _get_cache(self) -> RolesCache:
        # Create the cache if it doesn't already exist, and then return it.
        if not self.__cache:
            await self.__init_cache()
        assert self.__cache is not None
        return self.__cache

    async def _persist_changes(self):
        # Don't bother serializing or persisting unless we actually have a database.
        if self.database:
            cache = await self._get_cache()
            data = cache.serialize()
            await self.database.write(data)

    async def iter_role_entries(
        self, guild: Guild
    ) -> AsyncIterable[Tuple[RoleID, RolesRoleEntry]]:
        cache = await self._get_cache()
        for role_id, role_entry in cache.iter_role_entries(guild):
            yield role_id, role_entry

    async def get_role_entry(self, role: GuildRole) -> Optional[RolesRoleEntry]:
        cache = await self._get_cache()
        return cache.get_role_entry(role)

    async def add_role(
        self, role: GuildRole, joinable: bool, leavable: bool
    ) -> RolesRoleEntry:
        # Attempt to add the role to the cache.
        cache = await self._get_cache()
        if added_role_entry := cache.add_role(role, joinable, leavable):
            # If the role was indeed added to the cache, persist changes to the database
            # and return the added role entry so the caller knows the operation was
            # successful.
            await self._persist_changes()
            return added_role_entry

    async def remove_role(self, role: GuildRole) -> Optional[RolesRoleEntry]:
        # Attempt to remove the role entry from the cache.
        cache = await self._get_cache()
        if removed_role_entry := cache.remove_role(role):
            # If the role was indeed removed from the cache, persist changes to the
            # datbase and return the removed role entry so the caller know the operation
            # was successful.
            await self._persist_changes()
            return removed_role_entry
