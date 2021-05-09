from datetime import datetime
from typing import AsyncIterable, List, Optional, Protocol, Set, Tuple

from discord import Guild

from commanderbot_ext.lib import ResponsiveException


class InviteException(ResponsiveException):
    pass


class InviteKeyAlreadyExists(InviteException):
    def __init__(self, invite_key: str):
        self.invite_key: str = invite_key
        super().__init__(f"Invite `{invite_key}` already exists")


class NoSuchInvite(InviteException):
    def __init__(self, invite_key: str):
        self.invite_key: str = invite_key
        super().__init__(f"No such invite `{invite_key}`")


class InviteEntry(Protocol):
    key: str
    added_on: datetime
    modified_on: datetime
    hits: int
    link: str
    tags: Set[str]
    description: Optional[str]

    @property
    def sorted_tags(self) -> List[str]:
        ...


class InviteStore(Protocol):
    """
    Abstracts the data storage and persistence of the invite cog.
    """

    async def get_invite_entries(self, guild: Guild) -> List[InviteEntry]:
        ...

    async def require_invite_entry(self, guild: Guild, invite_key: str) -> InviteEntry:
        ...

    def query_invite_entries(
        self, guild: Guild, invite_query: str
    ) -> AsyncIterable[InviteEntry]:
        ...

    async def get_guild_invite_entry(self, guild: Guild) -> Optional[InviteEntry]:
        ...

    async def increment_invite_hits(self, invite_entry: InviteEntry):
        ...

    async def add_invite(self, guild: Guild, invite_key: str, link: str) -> InviteEntry:
        ...

    async def remove_invite(self, guild: Guild, invite_key: str) -> InviteEntry:
        ...

    async def modify_invite_link(
        self, guild: Guild, invite_key: str, link: str
    ) -> InviteEntry:
        ...

    async def modify_invite_tags(
        self, guild: Guild, invite_key: str, tags: Tuple[str, ...]
    ) -> InviteEntry:
        ...

    async def modify_invite_description(
        self, guild: Guild, invite_key: str, description: Optional[str]
    ) -> InviteEntry:
        ...

    async def configure_guild_key(
        self, guild: Guild, invite_key: Optional[str]
    ) -> Optional[InviteEntry]:
        ...
