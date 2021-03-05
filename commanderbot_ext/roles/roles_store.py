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
    database: Any

    role_entries_by_guild_id: Dict[GuildID, List[RolesRoleEntry]] = field(init=False)

    def __post_init__(self):
        self.role_entries_by_guild_id = {}

    def iter_role_entries(self, guild: Guild) -> Iterable[RolesRoleEntry]:
        yield from self.role_entries_by_guild_id.get(guild.id, [])

    def get_role_entry(self, role: Role) -> Optional[RolesRoleEntry]:
        guild: Guild = role.guild
        assert isinstance(guild, Guild)
        for entry in self.iter_role_entries(guild):
            if entry.role_id == role.id:
                return entry

    def resolve_role(self, guild: Guild, role_id: RoleID) -> Optional[Role]:
        role = guild.get_role(role_id)
        # If the role resolves correctly, return it.
        if isinstance(role, Role):
            return role
        # Otherwise skip it, but log so the role can be fixed.
        self.log.exception(f"Failed to resolve role ID: {role_id}")

    def iter_role_pairs(self, guild: Guild) -> Iterable[Tuple[Role, RolesRoleEntry]]:
        # Yield resolved roles alongside their corresponding entry, if any.
        for role_entry in self.iter_role_entries(guild):
            role = self.resolve_role(guild, role_entry.role_id)
            # Skip unresolved roles.
            if role:
                yield role, role_entry

    def get_sorted_role_pairs(self, guild: Guild) -> List[Tuple[Role, RolesRoleEntry]]:
        role_pairs = list(self.iter_role_pairs(guild))
        # Sort by stringified role name.
        sorted_role_pairs = sorted(role_pairs, key=lambda role_pair: str(role_pair[0]))
        return sorted_role_pairs
