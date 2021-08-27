from dataclasses import dataclass
from typing import AsyncIterable, List, Optional, Tuple

from discord import Guild, Role

from commanderbot_ext.ext.roles.roles_data import RolesData
from commanderbot_ext.ext.roles.roles_store import RoleEntry
from commanderbot_ext.lib import CogStore, GuildID, JsonFileDatabaseAdapter, RoleID


# @implements RolesStore
@dataclass
class RolesJsonStore(CogStore):
    """
    Implementation of `RolesStore` that uses a simple JSON file to persist state.
    """

    db: JsonFileDatabaseAdapter[RolesData]

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
