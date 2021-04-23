from datetime import datetime
from typing import AsyncIterable, Optional, Protocol, Tuple

from discord import Guild
from discord.ext.commands import Context

from commanderbot_ext.lib import GuildRole, ResponsiveException, RoleID


class RolesException(ResponsiveException):
    pass


class RoleNotRegistered(RolesException):
    def __init__(self, role: GuildRole):
        self.role: GuildRole = role
        super().__init__(f"Role `{role}` is not registered")

    async def respond(self, ctx: Context):
        await ctx.reply(f"🤷 `{self.role}` is not registered.")


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

    def iter_role_entries(
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
    ) -> RoleEntry:
        ...

    async def deregister_role(self, role: GuildRole) -> RoleEntry:
        ...
