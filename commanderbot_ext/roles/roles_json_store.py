import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterable, Dict, Iterable, Optional, Tuple

from discord import Guild

from commanderbot_ext._lib.cog_store import CogStore
from commanderbot_ext._lib.database_options import JsonFileDatabaseOptions
from commanderbot_ext._lib.types import GuildID, GuildRole, RoleID


@dataclass
class _RolesJsonRoleEntry:
    added_on: datetime
    joinable: bool
    leavable: bool

    @staticmethod
    def deserialize(data: dict) -> "_RolesJsonRoleEntry":
        return _RolesJsonRoleEntry(
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
class _RolesJsonGuildData:
    role_entries: Dict[RoleID, _RolesJsonRoleEntry]

    @staticmethod
    def deserialize(data: dict) -> "_RolesJsonGuildData":
        return _RolesJsonGuildData(
            role_entries={
                int(role_id): _RolesJsonRoleEntry.deserialize(raw_role_entry)
                for role_id, raw_role_entry in data.get("role_entries", {}).items()
            }
        )

    def serialize(self) -> dict:
        data = {}
        # Serialize role entries. Note that a role entry will never be empty, so we
        # include them all.
        role_entries = {
            str(role_id): role_entry.serialize()
            for role_id, role_entry in self.role_entries.items()
        }
        # Don't include an empty list of role entries.
        if role_entries:
            data["role_entries"] = role_entries
        return data

    def get_role_entry(self, role: GuildRole) -> Optional[_RolesJsonRoleEntry]:
        # Return the corresponding role entry, if any.
        return self.role_entries.get(role.id)

    def add_role(
        self, role: GuildRole, joinable: bool, leavable: bool
    ) -> _RolesJsonRoleEntry:
        # Create a new role entry and add it to the map. If the role is already present,
        # just replace it with the new information.
        added_role_entry = _RolesJsonRoleEntry(
            added_on=datetime.utcnow(),
            joinable=joinable,
            leavable=leavable,
        )
        self.role_entries[role.id] = added_role_entry
        # Return the newly-added role entry.
        return added_role_entry

    def remove_role(self, role: GuildRole) -> Optional[_RolesJsonRoleEntry]:
        # Pop and return the corresponding role entry, if any.
        return self.role_entries.pop(role.id, None)


@dataclass
class _RolesJson:
    guilds: Dict[GuildID, _RolesJsonGuildData]

    @staticmethod
    def deserialize(data: dict) -> "_RolesJson":
        return _RolesJson(
            guilds={
                int(guild_id): _RolesJsonGuildData.deserialize(raw_guild_data)
                for guild_id, raw_guild_data in data.get("guilds", {}).items()
            }
        )

    def serialize(self) -> dict:
        data = {}
        # Serialize guilds.
        guilds = {}
        for guild_id, guild_data in self.guilds.items():
            # Don't include empty guilds.
            if serialized_guild_data := guild_data.serialize():
                guilds[str(guild_id)] = serialized_guild_data
        # Don't include an empty list of guilds.
        if guilds:
            data["guilds"] = guilds
        return data

    def iter_role_entries(
        self, guild: Guild
    ) -> Iterable[Tuple[RoleID, _RolesJsonRoleEntry]]:
        # Get this guild's data, if any.
        if guild_data := self.guilds.get(guild.id):
            # Iterate over each role entry for this guild.
            for role_id, role_entry in guild_data.role_entries.items():
                yield role_id, role_entry

    def get_role_entry(self, role: GuildRole) -> Optional[_RolesJsonRoleEntry]:
        # Get this guild's data, if any.
        if guild_data := self.guilds.get(role.guild.id):
            # Return the corresponding role entry, if any.
            return guild_data.get_role_entry(role)

    def add_role(
        self, role: GuildRole, joinable: bool, leavable: bool
    ) -> _RolesJsonRoleEntry:
        # Get this guild's data, if any.
        guild_data = self.guilds.get(role.guild.id)
        # If this guild doesn't have data, initialize it.
        if not guild_data:
            guild_data = _RolesJsonGuildData({})
            self.guilds[role.guild.id] = guild_data
        # Add and return the role to the guild's role entries.
        return guild_data.add_role(role, joinable, leavable)

    def remove_role(self, role: GuildRole) -> Optional[_RolesJsonRoleEntry]:
        # Get this guild's data, if any.
        if guild_data := self.guilds.get(role.guild.id):
            # Remove and return the role from the guild's role entries, if it's there.
            return guild_data.remove_role(role)


@dataclass
class RolesJsonStore(CogStore):
    """
    Implementation of `RolesStore` that uses a simple JSON file to persist state.

    Alternatively: if a database is not provided, state will not be persisted,
    effectively turning this class into an in-memory database.
    """

    db_options: Optional[JsonFileDatabaseOptions] = None

    # Lazily-initialized in-memory representation of state. The reason this is lazy is
    # because it needs to be asynchronously initialized from within an async method.
    # **Do not use this member; use `_get_cache()` instead.**
    __cache: Optional[_RolesJson] = field(init=False, default=None)

    async def _create_cache(self) -> _RolesJson:
        if self.db_options:
            try:
                # TODO Async file I/O. #optimize
                with open(self.db_options.path) as fp:
                    data = json.load(fp)
                return _RolesJson.deserialize(data)
            except FileNotFoundError as ex:
                if self.db_options.auto_create:
                    self.log.warning(
                        f"Creating database file because it doesn't already exist: {self.db_options.path}"
                    )
                    # TODO Async file I/O. #optimize
                    self.db_options.path.parent.mkdir(parents=True, exist_ok=True)
                    with open(self.db_options.path, "w") as fp:
                        json.dump({}, fp)
                    return _RolesJson.deserialize({})
                else:
                    raise ex
        return _RolesJson.deserialize({})

    async def _get_cache(self) -> _RolesJson:
        # Create the cache if it doesn't already exist, and then return it.
        if not self.__cache:
            self.__cache = await self._create_cache()
        return self.__cache

    async def _dirty(self):
        cache = await self._get_cache()
        data = cache.serialize()
        # TODO Async file I/O. #optimize
        with open(self.db_options.path, "w") as fp:
            json.dump(data, fp, indent=2)

    # @implements RolesStore
    async def iter_role_entries(
        self, guild: Guild
    ) -> AsyncIterable[Tuple[RoleID, _RolesJsonRoleEntry]]:
        cache = await self._get_cache()
        for role_id, role_entry in cache.iter_role_entries(guild):
            yield role_id, role_entry

    # @implements RolesStore
    async def get_role_entry(self, role: GuildRole) -> Optional[_RolesJsonRoleEntry]:
        cache = await self._get_cache()
        return cache.get_role_entry(role)

    # @implements RolesStore
    async def add_role(
        self, role: GuildRole, joinable: bool, leavable: bool
    ) -> Optional[_RolesJsonRoleEntry]:
        # Attempt to add the role to the cache.
        cache = await self._get_cache()
        if added_role_entry := cache.add_role(role, joinable, leavable):
            # If the role was indeed added to the cache, mark as dirty and return the
            # added role entry so the caller knows the operation was successful.
            await self._dirty()
            return added_role_entry

    # @implements RolesStore
    async def remove_role(self, role: GuildRole) -> Optional[_RolesJsonRoleEntry]:
        # Attempt to remove the role entry from the cache.
        cache = await self._get_cache()
        if removed_role_entry := cache.remove_role(role):
            # If the role was indeed removed from the cache, mark as dirty and return
            # the removed role entry so the caller know the operation was successful.
            await self._dirty()
            return removed_role_entry
