from datetime import datetime
from typing import AsyncIterable, Optional, Protocol, Tuple

from discord import Guild

from commanderbot_ext._lib.types import GuildRole, RoleID


class RoleEntry(Protocol):
    added_on: datetime
    joinable: bool
    leavable: bool
    description: Optional[str]


RoleEntryPair = Tuple[GuildRole, RoleEntry]


class RolesStore(Protocol):
    """
    Abstracts the data storage and persistence of the roles cog.
    """

    async def iter_role_entries(
        self, guild: Guild
    ) -> AsyncIterable[Tuple[RoleID, RoleEntry]]:
        ...

    async def get_role_entry(self, role: GuildRole) -> Optional[RoleEntry]:
        ...

    async def register_role(
        self,
        role: GuildRole,
        joinable: bool,
        leavable: bool,
        description: Optional[str],
    ) -> Optional[RoleEntry]:
        ...

    async def deregister_role(self, role: GuildRole) -> Optional[RoleEntry]:
        ...
