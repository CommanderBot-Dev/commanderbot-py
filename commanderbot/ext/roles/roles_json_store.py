from dataclasses import dataclass
from typing import List, Optional

from discord import Guild, Role

from commanderbot.ext.roles.roles_data import RolesData
from commanderbot.ext.roles.roles_store import RoleEntry
from commanderbot.lib import (
    CogStore,
    GuildID,
    JsonFileDatabaseAdapter,
    RoleID,
    RoleSet,
)


# @implements RolesStore
@dataclass
class RolesJsonStore(CogStore):
    """
    Implementation of `RolesStore` that uses a simple JSON file to persist state.
    """

    db: JsonFileDatabaseAdapter[RolesData]

    # @implements RolesStore
    async def get_permitted_roles(self, guild: Guild) -> Optional[RoleSet]:
        cache = await self.db.get_cache()
        return await cache.get_permitted_roles(guild)

    # @implements RolesStore
    async def set_permitted_roles(
        self, guild: Guild, permitted_roles: Optional[RoleSet]
    ) -> Optional[RoleSet]:
        cache = await self.db.get_cache()
        old_value = await cache.set_permitted_roles(guild, permitted_roles)
        await self.db.dirty()
        return old_value

    # @implements RolesStore
    async def get_all_role_entries(self, guild: Guild) -> List[RoleEntry]:
        cache = await self.db.get_cache()
        return await cache.get_all_role_entries(guild)

    # @implements RolesStore
    async def get_role_entry(self, role: Role) -> Optional[RoleEntry]:
        cache = await self.db.get_cache()
        return await cache.get_role_entry(role)

    # @implements RolesStore
    async def register_role(
        self,
        role: Role,
        joinable: bool,
        leavable: bool,
        description: Optional[str],
    ) -> RoleEntry:
        cache = await self.db.get_cache()
        role_entry = await cache.register_role(
            role,
            joinable=joinable,
            leavable=leavable,
            description=description,
        )
        await self.db.dirty()
        return role_entry

    # @implements RolesStore
    async def deregister_role(self, role: Role) -> RoleEntry:
        cache = await self.db.get_cache()
        role_entry = await cache.deregister_role(role)
        await self.db.dirty()
        return role_entry

    # @implements RolesStore
    async def deregister_role_by_id(
        self, guild_id: GuildID, role_id: RoleID
    ) -> RoleEntry:
        cache = await self.db.get_cache()
        role_entry = await cache.deregister_role_by_id(guild_id, role_id)
        await self.db.dirty()
        return role_entry
