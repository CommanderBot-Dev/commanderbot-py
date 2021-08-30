from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import DefaultDict, Dict, List, Optional

from discord import Guild, Role

from commanderbot.ext.roles.roles_store import (
    RoleIDNotRegistered,
    RoleNotRegistered,
)
from commanderbot.lib import GuildID, JsonObject, RoleID
from commanderbot.lib.role_set import RoleSet
from commanderbot.lib.utils import dict_without_ellipsis


# @implements RoleEntry
@dataclass
class RoleEntryData:
    role_id: RoleID
    added_on: datetime
    joinable: bool
    leavable: bool
    description: Optional[str] = None

    @staticmethod
    def from_data(data: JsonObject) -> RoleEntryData:
        return RoleEntryData(
            role_id=int(data["role_id"]),
            added_on=datetime.fromisoformat(data["added_on"]),
            joinable=bool(data["joinable"]),
            leavable=bool(data["leavable"]),
            description=data.get("description"),
        )

    def to_data(self) -> JsonObject:
        return {
            "role_id": self.role_id,
            "added_on": self.added_on.isoformat(),
            "joinable": self.joinable,
            "leavable": self.leavable,
            "description": self.description,
        }


@dataclass
class RolesGuildData:
    # Index roles by ID for faster look-up in commands.
    role_entries: Dict[RoleID, RoleEntryData]

    # Roles that are permitted to manage the extension within this guild.
    permitted_roles: Optional[RoleSet] = None

    @staticmethod
    def from_data(data: JsonObject) -> RolesGuildData:
        role_entries_flat = [
            RoleEntryData.from_data(raw_entry)
            for raw_entry in data.get("role_entries", [])
        ]
        role_entries_map = {
            role_entry.role_id: role_entry for role_entry in role_entries_flat
        }
        permitted_roles = RoleSet.from_field_optional(data, "permitted_roles")
        return RolesGuildData(
            role_entries=role_entries_map,
            permitted_roles=permitted_roles,
        )

    def to_data(self) -> JsonObject:
        return dict_without_ellipsis(
            role_entries=[
                role_entry.to_data() for role_entry in self.role_entries.values()
            ]
            or ...,
            permitted_roles=self.permitted_roles or ...,
        )

    def set_permitted_roles(
        self, permitted_roles: Optional[RoleSet]
    ) -> Optional[RoleSet]:
        old_value = self.permitted_roles
        self.permitted_roles = permitted_roles
        return old_value

    def get_all_role_entries(self) -> List[RoleEntryData]:
        return list(self.role_entries.values())

    def get_role_entry(self, role: Role) -> Optional[RoleEntryData]:
        # Return the corresponding role entry, if any.
        return self.role_entries.get(role.id)

    def register_role(
        self,
        role: Role,
        joinable: bool,
        leavable: bool,
        description: Optional[str],
    ) -> RoleEntryData:
        # Create a new role entry and add it to the map. If the role is already present,
        # just replace it with the new information.
        added_role_entry = RoleEntryData(
            role_id=role.id,
            added_on=datetime.utcnow(),
            joinable=joinable,
            leavable=leavable,
            description=description,
        )
        self.role_entries[role.id] = added_role_entry
        # Return the newly-added role entry.
        return added_role_entry

    def deregister_role(self, role: Role) -> RoleEntryData:
        # Remove and return the role entry, if it exists.
        if role_entry := self.role_entries.pop(role.id, None):
            return role_entry
        # Otherwise, if it does not exist, raise.
        raise RoleNotRegistered(role)

    def deregister_role_by_id(self, role_id: RoleID) -> RoleEntryData:
        # Remove and return the role entry, if it exists.
        if role_entry := self.role_entries.pop(role_id, None):
            return role_entry
        # Otherwise, if it does not exist, raise.
        raise RoleIDNotRegistered(role_id)


def _guilds_defaultdict_factory() -> DefaultDict[GuildID, RolesGuildData]:
    return defaultdict(lambda: RolesGuildData(role_entries={}))


# @implements RolesStore
@dataclass
class RolesData:
    """
    Implementation of `RolesStore` using an in-memory object hierarchy.
    """

    guilds: DefaultDict[GuildID, RolesGuildData] = field(
        default_factory=_guilds_defaultdict_factory
    )

    @staticmethod
    def from_data(data: JsonObject) -> RolesData:
        guilds = _guilds_defaultdict_factory()
        guilds.update(
            {
                int(guild_id): RolesGuildData.from_data(raw_guild_data)
                for guild_id, raw_guild_data in data.get("guilds", {}).items()
            }
        )
        return RolesData(guilds=guilds)

    def to_data(self) -> JsonObject:
        # Omit empty guilds, as well as an empty list of guilds.
        return dict_without_ellipsis(
            guilds=dict_without_ellipsis(
                {
                    str(guild_id): (guild_data.to_data() or ...)
                    for guild_id, guild_data in self.guilds.items()
                }
            )
            or ...
        )

    # @implements RolesStore
    async def get_permitted_roles(self, guild: Guild) -> Optional[RoleSet]:
        return self.guilds[guild.id].permitted_roles

    # @implements RolesStore
    async def set_permitted_roles(
        self, guild: Guild, permitted_roles: Optional[RoleSet]
    ) -> Optional[RoleSet]:
        return self.guilds[guild.id].set_permitted_roles(permitted_roles)

    # @implements RolesStore
    async def get_role_entries(self, guild: Guild) -> List[RoleEntryData]:
        for role_id, role_entry in self.guilds[guild.id].role_entries.items():
            yield role_id, role_entry

    # @implements RolesStore
    async def get_all_role_entries(self, guild: Guild) -> List[RoleEntryData]:
        return self.guilds[guild.id].get_all_role_entries()

    # @implements RolesStore
    async def get_role_entry(self, role: Role) -> Optional[RoleEntryData]:
        return self.guilds[role.guild.id].get_role_entry(role)

    # @implements RolesStore
    async def register_role(
        self,
        role: Role,
        joinable: bool,
        leavable: bool,
        description: Optional[str],
    ) -> RoleEntryData:
        return self.guilds[role.guild.id].register_role(
            role,
            joinable=joinable,
            leavable=leavable,
            description=description,
        )

    # @implements RolesStore
    async def deregister_role(self, role: Role) -> RoleEntryData:
        return self.guilds[role.guild.id].deregister_role(role)

    # @implements RolesStore
    async def deregister_role_by_id(
        self, guild_id: GuildID, role_id: RoleID
    ) -> RoleEntryData:
        return self.guilds[guild_id].deregister_role_by_id(role_id)
