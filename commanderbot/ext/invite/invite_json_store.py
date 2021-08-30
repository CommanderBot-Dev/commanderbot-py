from dataclasses import dataclass
from typing import AsyncIterable, List, Optional, Tuple

from discord import Guild

from commanderbot_ext.ext.invite.invite_data import InviteData
from commanderbot_ext.ext.invite.invite_store import InviteEntry
from commanderbot_ext.lib import CogStore, JsonFileDatabaseAdapter


# @implements InviteStore
@dataclass
class InviteJsonStore(CogStore):
    """
    Implementation of `InviteStore` that uses a simple JSON file to persist state.
    """

    db: JsonFileDatabaseAdapter[InviteData]

    # @implements InviteStore
    async def get_invite_entries(self, guild: Guild) -> List[InviteEntry]:
        cache = await self.db.get_cache()
        return await cache.get_invite_entries(guild)

    # @implements InviteStore
    async def require_invite_entry(self, guild: Guild, invite_key: str) -> InviteEntry:
        cache = await self.db.get_cache()
        return await cache.require_invite_entry(guild, invite_key)

    # @implements InviteStore
    async def query_invite_entries(
        self, guild: Guild, invite_query: str
    ) -> AsyncIterable[InviteEntry]:
        cache = await self.db.get_cache()
        async for invite_entry in cache.query_invite_entries(guild, invite_query):
            yield invite_entry

    # @implements InviteStore
    async def get_guild_invite_entry(self, guild: Guild) -> Optional[InviteEntry]:
        cache = await self.db.get_cache()
        return await cache.get_guild_invite_entry(guild)

    # @implements InviteStore
    async def increment_invite_hits(self, invite_entry: InviteEntry):
        cache = await self.db.get_cache()
        await cache.increment_invite_hits(invite_entry)
        await self.db.dirty()

    # @implements InviteStore
    async def add_invite(self, guild: Guild, invite_key: str, link: str) -> InviteEntry:
        cache = await self.db.get_cache()
        invite_entry = await cache.add_invite(guild, invite_key, link=link)
        await self.db.dirty()
        return invite_entry

    # @implements InviteStore
    async def remove_invite(self, guild: Guild, invite_key: str) -> InviteEntry:
        cache = await self.db.get_cache()
        invite_entry = await cache.remove_invite(guild, invite_key)
        await self.db.dirty()
        return invite_entry

    # @implements InviteStore
    async def modify_invite_link(
        self, guild: Guild, invite_key: str, link: str
    ) -> InviteEntry:
        cache = await self.db.get_cache()
        invite_entry = await cache.modify_invite_link(guild, invite_key, link)
        await self.db.dirty()
        return invite_entry

    # @implements InviteStore
    async def modify_invite_tags(
        self, guild: Guild, invite_key: str, tags: Tuple[str, ...]
    ) -> InviteEntry:
        cache = await self.db.get_cache()
        invite_entry = await cache.modify_invite_tags(guild, invite_key, tags)
        await self.db.dirty()
        return invite_entry

    async def modify_invite_description(
        self, guild: Guild, invite_key: str, description: Optional[str]
    ) -> InviteEntry:
        cache = await self.db.get_cache()
        invite_entry = await cache.modify_invite_description(
            guild, invite_key, description
        )
        await self.db.dirty()
        return invite_entry

    # @implements InviteStore
    async def configure_guild_key(
        self, guild: Guild, invite_key: Optional[str]
    ) -> Optional[InviteEntry]:
        cache = await self.db.get_cache()
        invite_entry = await cache.configure_guild_key(guild, invite_key)
        await self.db.dirty()
        return invite_entry
