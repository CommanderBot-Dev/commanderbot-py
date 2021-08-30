from datetime import datetime
from typing import List, Optional, Protocol, Tuple

from discord import Guild, Role

from commanderbot.lib import GuildID, ResponsiveException, RoleID, RoleSet


class RolesException(ResponsiveException):
    pass


class RoleNotRegistered(RolesException):
    def __init__(self, role: Role):
        self.role: Role = role
        message = f"🤷 {role.mention} is not registered."
        super().__init__(message)


class RoleIDNotRegistered(RolesException):
    def __init__(self, role_id: RoleID):
        self.role_id: RoleID = role_id
        message = f"🤷 No role with ID `{role_id}` is registered."
        super().__init__(message)


class RoleEntry(Protocol):
    role_id: RoleID
    added_on: datetime
    joinable: bool
    leavable: bool
    description: Optional[str]


RoleEntryPair = Tuple[Role, RoleEntry]


class RolesStore(Protocol):
    """
    Abstracts the data storage and persistence of the roles cog.
    """

    async def get_permitted_roles(self, guild: Guild) -> Optional[RoleSet]:
        ...

    async def set_permitted_roles(
        self, guild: Guild, permitted_roles: Optional[RoleSet]
    ) -> Optional[RoleSet]:
        ...

    async def get_all_role_entries(self, guild: Guild) -> List[RoleEntry]:
        ...

    async def get_role_entry(self, role: Role) -> Optional[RoleEntry]:
        ...

    async def register_role(
        self,
        role: Role,
        joinable: bool,
        leavable: bool,
        description: Optional[str],
    ) -> RoleEntry:
        ...

    async def deregister_role(self, role: Role) -> RoleEntry:
        ...

    async def deregister_role_by_id(
        self, guild_id: GuildID, role_id: RoleID
    ) -> RoleEntry:
        ...
