from datetime import datetime
from typing import AsyncIterable, Optional, Protocol, Tuple

from discord import Guild

from commanderbot_ext._lib.types import GuildRole, RoleID


class RoleEntry(Protocol):
    added_on: datetime
    joinable: bool
    leavable: bool


RoleEntryPair = Tuple[GuildRole, RoleEntry]


class RolesStore(Protocol):
    async def iter_role_entries(
        self, guild: Guild
    ) -> AsyncIterable[Tuple[RoleID, RoleEntry]]:
        ...

    async def get_role_entry(self, role: GuildRole) -> Optional[RoleEntry]:
        ...

    async def add_role(
        self, role: GuildRole, joinable: bool, leavable: bool
    ) -> Optional[RoleEntry]:
        ...

    async def remove_role(self, role: GuildRole) -> Optional[RoleEntry]:
        ...
