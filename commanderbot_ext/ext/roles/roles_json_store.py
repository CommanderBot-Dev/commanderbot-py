from dataclasses import dataclass
from typing import AsyncIterable, Optional, Tuple

from discord import Guild, Message, PartialEmoji, User, Role

from commanderbot_ext.ext.roles.roles_data import RolesData
from commanderbot_ext.ext.roles.roles_store import RoleEntry
from commanderbot_ext.lib import CogStore, GuildRole, JsonFileDatabaseAdapter, RoleID


# @implements RolesStore
@dataclass
class RolesJsonStore(CogStore):
    """
    Implementation of `RolesStore` that uses a simple JSON file to persist state.
    """

    db: JsonFileDatabaseAdapter[RolesData]
    
    # @implements RolesStore
    async def process_reaction(self, guild: Guild, emoji: PartialEmoji, msg: Message) -> Optional[Role]:
        async for role_id, entry in self.iter_role_entries(guild):
            print(f"{role_id}, {entry}")
            if entry.is_reaction_targeted(str(emoji), msg.id):
                return guild.get_role(role_id)
        return None

    # @implements RolesStore
    async def iter_role_entries(
        self, guild: Guild
    ) -> AsyncIterable[Tuple[RoleID, RoleEntry]]:
        cache = await self.db.get_cache()
        async for role_id, role_entry in cache.iter_role_entries(guild):
            yield role_id, role_entry

    # @implements RolesStore
    async def get_role_entry(self, role: GuildRole) -> Optional[RoleEntry]:
        cache = await self.db.get_cache()
        return await cache.get_role_entry(role)

    # @implements RolesStore
    async def register_role(
        self,
        role: GuildRole,
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
    async def deregister_role(self, role: GuildRole) -> RoleEntry:
        cache = await self.db.get_cache()
        role_entry = await cache.deregister_role(role)
        await self.db.dirty()
        return role_entry

    async def react_role(self, role: GuildRole, msg: Message, emoji: str) -> RoleEntry:
        cache = await self.db.get_cache()
        role_entry = await cache.react_role(role, msg, emoji)
        await self.db.dirty()
        return role_entry