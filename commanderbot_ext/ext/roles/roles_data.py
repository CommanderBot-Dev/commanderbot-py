from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterable, DefaultDict, Dict, Optional, Tuple

from discord import Guild

from commanderbot_ext.ext.roles.roles_store import RoleNotRegistered
from commanderbot_ext.lib import GuildID, GuildRole, JsonObject, RoleID
from commanderbot_ext.lib.utils import dict_without_falsies


# @implements RoleEntry
@dataclass
class RolesDataRoleEntry:
    added_on: datetime
    joinable: bool
    leavable: bool
    description: Optional[str] = None

    @staticmethod
    def deserialize(data: JsonObject) -> "RolesDataRoleEntry":
        return RolesDataRoleEntry(
            added_on=datetime.fromisoformat(data["added_on"]),
            joinable=bool(data["joinable"]),
            leavable=bool(data["leavable"]),
            description=data.get("description"),
        )

    def serialize(self) -> JsonObject:
        return {
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
        return RolesDataGuild(
            role_entries={
                int(role_id): RolesDataRoleEntry.deserialize(raw_entry)
                for role_id, raw_entry in data.get("role_entries", {}).items()
            }
        )

    def serialize(self) -> JsonObject:
        return dict_without_falsies(
            role_entries={
                str(role_id): role_entry.serialize()
                for role_id, role_entry in self.role_entries.items()
            }
        )

    def get_role_entry(self, role: GuildRole) -> Optional[RolesDataRoleEntry]:
        # Return the corresponding role entry, if any.
        return self.role_entries.get(role.id)

    def register_role(
        self,
        role: GuildRole,
        joinable: bool,
        leavable: bool,
        description: Optional[str],
    ) -> RolesDataRoleEntry:
        # Create a new role entry and add it to the map. If the role is already present,
        # just replace it with the new information.
        added_role_entry = RolesDataRoleEntry(
            added_on=datetime.utcnow(),
            joinable=joinable,
            leavable=leavable,
            description=description,
        )
        self.role_entries[role.id] = added_role_entry
        # Return the newly-added role entry.
        return added_role_entry

    def deregister_role(self, role: GuildRole) -> RolesDataRoleEntry:
        # Remove and return the role entry, if it exists.
        if role_entry := self.role_entries.pop(role.id, None):
            return role_entry
        # Otherwise, if it does not exist, raise.
        raise RoleNotRegistered(role)


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
    async def iter_role_entries(
        self, guild: Guild
    ) -> AsyncIterable[Tuple[RoleID, RolesDataRoleEntry]]:
        for role_id, role_entry in self.guilds[guild.id].role_entries.items():
            yield role_id, role_entry

    # @implements RolesStore
    async def get_role_entry(self, role: GuildRole) -> Optional[RolesDataRoleEntry]:
        return self.guilds[role.guild.id].get_role_entry(role)

    # @implements RolesStore
    async def register_role(
        self,
        role: GuildRole,
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
    async def deregister_role(self, role: GuildRole) -> RolesDataRoleEntry:
        return self.guilds[role.guild.id].deregister_role(role)
