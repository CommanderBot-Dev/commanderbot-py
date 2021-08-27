from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterable, DefaultDict, Dict, List, Optional, Tuple

from discord import Guild, Role

from commanderbot_ext.ext.roles.roles_store import (
    RoleIDNotRegistered,
    RoleNotRegistered,
)
from commanderbot_ext.lib import GuildID, JsonObject, RoleID
from commanderbot_ext.lib.utils import dict_without_falsies


# @implements RoleEntry
@dataclass
class RolesDataRoleEntry:
    role_id: RoleID
    added_on: datetime
    joinable: bool
    leavable: bool
    description: Optional[str] = None

    @staticmethod
    def deserialize(data: JsonObject) -> "RolesDataRoleEntry":
        return RolesDataRoleEntry(
            role_id=int(data["role_id"]),
            added_on=datetime.fromisoformat(data["added_on"]),
            joinable=bool(data["joinable"]),
            leavable=bool(data["leavable"]),
            description=data.get("description"),
        )

    def serialize(self) -> JsonObject:
        return {
            "role_id": self.role_id,
            "added_on": self.added_on.isoformat(),
            "joinable": self.joinable,
            "leavable": self.leavable,
            "description": self.description,
        }


@dataclass
class RolesDataGuild:
    role_entries: Dict[RoleID, RolesDataRoleEntry]

    @staticmethod
    def deserialize(data: JsonObject) -> "RolesDataGuild":
        role_entries_flat = [
            RolesDataRoleEntry.deserialize(raw_entry)
            for raw_entry in data.get("role_entries", [])
        ]
        role_entries_map = {
            role_entry.role_id: role_entry for role_entry in role_entries_flat
        }
        return RolesDataGuild(role_entries=role_entries_map)

    def serialize(self) -> JsonObject:
        return dict_without_falsies(
            role_entries=[
                role_entry.serialize() for role_entry in self.role_entries.values()
            ]
        )

    def get_all_role_entries(self) -> List[RolesDataRoleEntry]:
        return list(self.role_entries.values())

    def get_role_entry(self, role: Role) -> Optional[RolesDataRoleEntry]:
        # Return the corresponding role entry, if any.
        return self.role_entries.get(role.id)

    def register_role(
        self,
        role: Role,
        joinable: bool,
        leavable: bool,
        description: Optional[str],
    ) -> RolesDataRoleEntry:
        # Create a new role entry and add it to the map. If the role is already present,
        # just replace it with the new information.
        added_role_entry = RolesDataRoleEntry(
            role_id=role.id,
            added_on=datetime.utcnow(),
            joinable=joinable,
            leavable=leavable,
            description=description,
        )
        self.role_entries[role.id] = added_role_entry
        # Return the newly-added role entry.
        return added_role_entry

    def deregister_role(self, role: Role) -> RolesDataRoleEntry:
        # Remove and return the role entry, if it exists.
        if role_entry := self.role_entries.pop(role.id, None):
            return role_entry
        # Otherwise, if it does not exist, raise.
        raise RoleNotRegistered(role)

    def deregister_role_by_id(self, role_id: RoleID) -> RolesDataRoleEntry:
        # Remove and return the role entry, if it exists.
        if role_entry := self.role_entries.pop(role_id, None):
            return role_entry
        # Otherwise, if it does not exist, raise.
        raise RoleIDNotRegistered(role_id)


def _guilds_defaultdict_factory() -> DefaultDict[GuildID, RolesDataGuild]:
    return defaultdict(lambda: RolesDataGuild(role_entries={}))


# @implements RolesStore
@dataclass
class RolesData:
    """
    Implementation of `RolesStore` using an in-memory object hierarchy.
    """

    guilds: DefaultDict[GuildID, RolesDataGuild] = field(
        default_factory=_guilds_defaultdict_factory
    )

    @staticmethod
    def deserialize(data: JsonObject) -> "RolesData":
        guilds = _guilds_defaultdict_factory()
        guilds.update(
            {
                int(guild_id): RolesDataGuild.deserialize(raw_guild_data)
                for guild_id, raw_guild_data in data.get("guilds", {}).items()
            }
        )
        return RolesData(guilds=guilds)

    def serialize(self) -> JsonObject:
        # Omit empty guilds, as well as an empty list of guilds.
        return dict_without_falsies(
            guilds=dict_without_falsies(
                {
                    str(guild_id): guild_data.serialize()
                    for guild_id, guild_data in self.guilds.items()
                }
            )
        )

    # @implements RolesStore
    async def get_role_entries(self, guild: Guild) -> List[RolesDataRoleEntry]:
        for role_id, role_entry in self.guilds[guild.id].role_entries.items():
            yield role_id, role_entry

    # @implements RolesStore
    async def get_all_role_entries(self, guild: Guild) -> List[RolesDataRoleEntry]:
        return self.guilds[guild.id].get_all_role_entries()

    # @implements RolesStore
    async def get_role_entry(self, role: Role) -> Optional[RolesDataRoleEntry]:
        return self.guilds[role.guild.id].get_role_entry(role)

    # @implements RolesStore
    async def register_role(
        self,
        role: Role,
        joinable: bool,
        leavable: bool,
        description: Optional[str],
    ) -> RolesDataRoleEntry:
        return self.guilds[role.guild.id].register_role(
            role,
            joinable=joinable,
            leavable=leavable,
            description=description,
        )

    # @implements RolesStore
    async def deregister_role(self, role: Role) -> RolesDataRoleEntry:
        return self.guilds[role.guild.id].deregister_role(role)

    # @implements RolesStore
    async def deregister_role_by_id(
        self, guild_id: GuildID, role_id: RoleID
    ) -> RolesDataRoleEntry:
        return self.guilds[guild_id].deregister_role_by_id(role_id)
