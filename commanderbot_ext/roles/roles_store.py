from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from discord import Guild, Role

from commanderbot_ext._lib.cog_store import CogStore
from commanderbot_ext._lib.types import GuildID, RoleID


@dataclass
class RolesRoleEntry:
    role_id: RoleID
    added_on: datetime
    joinable: bool


@dataclass
class RolesStore(CogStore):
    # IMPL Actually use the database to persist changes.
    database: Any

    role_entries_by_guild_id: Dict[GuildID, Dict[RoleID, RolesRoleEntry]] = field(
        init=False
    )

    def __post_init__(self):
        self.role_entries_by_guild_id = {}

    def iter_role_entries(self, guild: Guild) -> Iterable[RolesRoleEntry]:
        yield from self.role_entries_by_guild_id.get(guild.id, {}).values()

    def resolve_role(self, guild: Guild, role_id: RoleID) -> Optional[Role]:
        # Attempt to resolve the role from the given ID.
        role = guild.get_role(role_id)
        # If the role resolves correctly, return it.
        if isinstance(role, Role):
            return role
        # Otherwise skip it, but log so the role can be fixed.
        self.log.exception(f"Failed to resolve role ID: {role_id}")

    def iter_role_pairs(self, guild: Guild) -> Iterable[Tuple[Role, RolesRoleEntry]]:
        # Yield resolved roles alongside their corresponding entry, if any.
        for role_entry in self.iter_role_entries(guild):
            # Attempt to resolve the role from the role entry's role ID.
            role = self.resolve_role(guild, role_entry.role_id)
            # Skip the role if it wasn't resolved.
            if role is not None:
                yield role, role_entry

    def get_sorted_role_pairs(self, guild: Guild) -> List[Tuple[Role, RolesRoleEntry]]:
        # Flatten role pairs into a list.
        role_pairs = list(self.iter_role_pairs(guild))
        # Sort by stringified role name.
        sorted_role_pairs = sorted(role_pairs, key=lambda role_pair: str(role_pair[0]))
        return sorted_role_pairs

    def get_role_entry(self, role: Role) -> Optional[RolesRoleEntry]:
        # We ought to have a valid role/guild.
        guild: Guild = role.guild
        assert isinstance(guild, Guild)
        # Get the role entries for this guild.
        guild_role_entries = self.role_entries_by_guild_id.get(guild.id)
        # Return the corresponding role entry, if any.
        return guild_role_entries.get(role.id)

    def add_role(self, role: Role, joinable: bool) -> Optional[RolesRoleEntry]:
        # We ought to have a valid role/guild.
        guild = role.guild
        assert isinstance(guild, Guild)
        # Get the role entries for this guild.
        guild_role_entries = self.role_entries_by_guild_id.get(guild.id)
        # Create a new map if this guild doesn't already have one.
        if guild_role_entries is None:
            guild_role_entries = {}
            self.role_entries_by_guild_id[guild.id] = guild_role_entries
        # Make sure the role isn't already in the map.
        if role.id not in guild_role_entries:
            # Create a new role entry and add it to the map.
            new_role_entry = RolesRoleEntry(
                role_id=role.id, added_on=datetime.utcnow(), joinable=joinable
            )
            guild_role_entries[role.id] = new_role_entry
            # Return it so the caller knows it's just been added.
            return new_role_entry

    def remove_role(self, role: Role) -> Optional[RolesRoleEntry]:
        # We ought to have a valid role/guild.
        guild = role.guild
        assert isinstance(guild, Guild)
        # Get the role entries for this guild.
        guild_role_entries = self.role_entries_by_guild_id.get(guild.id)
        # Make sure the guild actually has entries.
        if guild_role_entries:
            # Attempt to pop the role entry from the map. If it's in the map, it will be
            # returned, so the caller knows it's just been removed.
            return guild_role_entries.pop(role.id, None)
