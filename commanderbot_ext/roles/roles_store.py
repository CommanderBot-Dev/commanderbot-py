from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from discord import Guild, Role

from commanderbot_ext._lib.cog_store import CogStore
from commanderbot_ext._lib.types import GuildID, RoleID


@dataclass
class RolesRoleEntry:
    role_id: RoleID
    added_on: datetime
    joinable: bool
    leavable: bool


@dataclass
class RolesStore(CogStore):
    # IMPL Actually use the database to persist changes.
    database: Any

    _role_entries_by_guild_id: Dict[GuildID, Dict[RoleID, RolesRoleEntry]] = field(
        init=False
    )

    def __post_init__(self):
        self._role_entries_by_guild_id = {}

    def iter_role_entries(self, guild: Guild) -> Iterable[RolesRoleEntry]:
        yield from self._role_entries_by_guild_id.get(guild.id, {}).values()

    def get_role_entry(self, role: Role) -> Optional[RolesRoleEntry]:
        # We ought to have a valid role/guild.
        guild: Guild = role.guild
        assert isinstance(guild, Guild)
        # Get the role entries for this guild.
        guild_role_entries = self._role_entries_by_guild_id.get(guild.id, {})
        # Return the corresponding role entry, if any.
        return guild_role_entries.get(role.id)

    def add_role(self, role: Role, joinable: bool, leavable: bool) -> RolesRoleEntry:
        # We ought to have a valid role/guild.
        guild = role.guild
        assert isinstance(guild, Guild)
        # Get the role entries for this guild.
        guild_role_entries = self._role_entries_by_guild_id.get(guild.id)
        # Create a new map if this guild doesn't already have one.
        if guild_role_entries is None:
            guild_role_entries = {}
            self._role_entries_by_guild_id[guild.id] = guild_role_entries
        # Create a new role entry and add it to the map. If the role is already in the
        # map, we're fine to just replace it with the new information.
        new_role_entry = RolesRoleEntry(
            role_id=role.id,
            added_on=datetime.utcnow(),
            joinable=joinable,
            leavable=leavable,
        )
        guild_role_entries[role.id] = new_role_entry
        # Return it so the caller knows it's just been added.
        return new_role_entry

    def remove_role(self, role: Role) -> Optional[RolesRoleEntry]:
        # We ought to have a valid role/guild.
        guild = role.guild
        assert isinstance(guild, Guild)
        # Get the role entries for this guild.
        guild_role_entries = self._role_entries_by_guild_id.get(guild.id)
        # Make sure the guild actually has entries.
        if guild_role_entries:
            # Attempt to pop the role entry from the map. If it's in the map, it will be
            # returned, so the caller knows it's just been removed.
            return guild_role_entries.pop(role.id, None)
