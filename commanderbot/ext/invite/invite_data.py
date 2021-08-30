from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import (
    AsyncIterable,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
)

from discord import Guild

from commanderbot_ext.ext.invite.invite_store import (
    InviteEntry,
    InviteKeyAlreadyExists,
    NoSuchInvite,
)
from commanderbot_ext.lib import GuildID, JsonObject
from commanderbot_ext.lib.utils import dict_without_falsies


# @implements InviteEntry
@dataclass
class InviteDataInviteEntry:
    key: str
    added_on: datetime
    modified_on: datetime
    hits: int
    link: str
    tags: Set[str]
    description: Optional[str]

    @staticmethod
    def deserialize(data: JsonObject, key: str) -> "InviteDataInviteEntry":
        return InviteDataInviteEntry(
            key=key,
            added_on=datetime.fromisoformat(data["added_on"]),
            modified_on=datetime.fromisoformat(data["modified_on"]),
            hits=data["hits"],
            link=data["link"],
            tags=set(data["tags"]),
            description=data.get("description"),
        )

    def serialize(self) -> JsonObject:
        return {
            "added_on": self.added_on.isoformat(),
            "modified_on": self.modified_on.isoformat(),
            "hits": self.hits,
            "link": self.link,
            "tags": list(self.tags),
            "description": self.description,
        }

    # @implements InviteEntry
    @property
    def sorted_tags(self) -> List[str]:
        return sorted(self.tags)

    def update_modified_on(self) -> datetime:
        self.modified_on = datetime.utcnow()
        return self.modified_on


@dataclass
class InviteDataGuild:
    invite_entries: Dict[str, InviteDataInviteEntry] = field(default_factory=dict)
    guild_key: Optional[str] = None

    invite_entries_by_tag: DefaultDict[str, List[InviteDataInviteEntry]] = field(
        init=False, default_factory=lambda: defaultdict(list)
    )

    @property
    def guild_invite_entry(self) -> Optional[InviteDataInviteEntry]:
        if self.guild_key:
            return self.invite_entries[self.guild_key]

    @staticmethod
    def deserialize(data: JsonObject) -> "InviteDataGuild":
        # Note that tags will be constructed from entries, during post-init.
        return InviteDataGuild(
            guild_key=data.get("guild_key"),
            invite_entries={
                key: InviteDataInviteEntry.deserialize(raw_entry, key)
                for key, raw_entry in data.get("invite_entries", {}).items()
            },
        )

    def __post_init__(self):
        # Build the list of tags from entries.
        for entry in self.invite_entries.values():
            for tag in entry.tags:
                self.invite_entries_by_tag[tag].append(entry)

    def _is_invite_key_available(self, invite_key: str) -> bool:
        # Check whether the given invite key is already in use.
        return invite_key not in self.invite_entries

    def _get_tags_from_query(self, invite_query: str) -> Set[str]:
        return set(invite_query.split())

    def serialize(self) -> JsonObject:
        return dict_without_falsies(
            guild_key=self.guild_key,
            invite_entries={
                key: entry.serialize() for key, entry in self.invite_entries.items()
            },
        )

    def require_invite_entry(self, invite_key: str) -> InviteDataInviteEntry:
        # Return the invite entry, if it exists.
        if invite_entry := self.invite_entries.get(invite_key):
            return invite_entry
        # Otherwise, raise.
        raise NoSuchInvite(invite_key)

    def query_invite_entries(
        self, invite_query: str
    ) -> Iterable[InviteDataInviteEntry]:
        # First, check for an exact match by key.
        if by_key := self.invite_entries.get(invite_query):
            yield by_key
        # Next, check for any number of matches by tags.
        elif tags := self._get_tags_from_query(invite_query):
            # Yield invite entries that have *any* of the tags.
            for invite_entry in self.invite_entries.values():
                if tags.intersection(invite_entry.tags):
                    yield invite_entry

    def add_invite(self, invite_key: str, link: str) -> InviteDataInviteEntry:
        # Ensure the given key is available.
        if not self._is_invite_key_available(invite_key):
            raise InviteKeyAlreadyExists(invite_key)
        # Create and register a new invite entry.
        now = datetime.utcnow()
        invite_entry = InviteDataInviteEntry(
            key=invite_key,
            added_on=now,
            modified_on=now,
            hits=0,
            link=link,
            tags=set(),
            description="",
        )
        self.invite_entries[invite_key] = invite_entry
        # Return the newly-created invite entry.
        return invite_entry

    def remove_invite(self, invite_key: str) -> InviteDataInviteEntry:
        # Remove and return the invite entry, if it exists.
        if invite_entry := self.invite_entries.pop(invite_key, None):
            # Remove the guild key, if necessary.
            if self.guild_key == invite_entry.key:
                self.guild_key = None
            # Return the invite entry.
            return invite_entry
        # Otherwise, if it does not exist, raise.
        raise NoSuchInvite(invite_key)

    def modify_invite_link(self, invite_key: str, link: str) -> InviteDataInviteEntry:
        invite_entry = self.require_invite_entry(invite_key)
        invite_entry.update_modified_on()
        invite_entry.link = link
        return invite_entry

    def modify_invite_tags(
        self, invite_key: str, tags: Tuple[str, ...]
    ) -> InviteDataInviteEntry:
        invite_entry = self.require_invite_entry(invite_key)
        invite_entry.tags = set(tags)
        return invite_entry

    def modify_invite_description(
        self, invite_key: str, description: Optional[str]
    ) -> InviteDataInviteEntry:
        invite_entry = self.require_invite_entry(invite_key)
        invite_entry.description = description
        return invite_entry

    def configure_guild_key(self, invite_key: Optional[str]) -> Optional[InviteEntry]:
        if not invite_key:
            self.guild_key = None
            return
        invite_entry = self.require_invite_entry(invite_key)
        self.guild_key = invite_key
        return invite_entry


def _guilds_defaultdict_factory() -> DefaultDict[GuildID, InviteDataGuild]:
    return defaultdict(lambda: InviteDataGuild())


# @implements InviteStore
@dataclass
class InviteData:
    """
    Implementation of `InviteStore` using an in-memory object hierarchy.
    """

    guilds: DefaultDict[GuildID, InviteDataGuild] = field(
        default_factory=_guilds_defaultdict_factory
    )

    @staticmethod
    def deserialize(data: JsonObject) -> "InviteData":
        guilds = _guilds_defaultdict_factory()
        guilds.update(
            {
                int(guild_id): InviteDataGuild.deserialize(raw_guild_data)
                for guild_id, raw_guild_data in data.get("guilds", {}).items()
            }
        )
        return InviteData(guilds=guilds)

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

    # @implements InviteStore
    async def get_invite_entries(self, guild: Guild) -> List[InviteEntry]:
        return [
            invite_entry
            for invite_entry in self.guilds[guild.id].invite_entries.values()
        ]

    # @implements InviteStore
    async def require_invite_entry(self, guild: Guild, invite_key: str) -> InviteEntry:
        return self.guilds[guild.id].require_invite_entry(invite_key)

    # @implements InviteStore
    async def query_invite_entries(
        self, guild: Guild, invite_query: str
    ) -> AsyncIterable[InviteEntry]:
        for invite_entry in self.guilds[guild.id].query_invite_entries(invite_query):
            yield invite_entry

    # @implements InviteStore
    async def get_guild_invite_entry(self, guild: Guild) -> Optional[InviteEntry]:
        return self.guilds[guild.id].guild_invite_entry

    # @implements InviteStore
    async def increment_invite_hits(self, invite_entry: InviteEntry):
        invite_entry.hits += 1

    # @implements InviteStore
    async def add_invite(self, guild: Guild, invite_key: str, link: str) -> InviteEntry:
        return self.guilds[guild.id].add_invite(invite_key, link=link)

    # @implements InviteStore
    async def remove_invite(self, guild: Guild, invite_key: str) -> InviteEntry:
        return self.guilds[guild.id].remove_invite(invite_key)

    # @implements InviteStore
    async def modify_invite_link(
        self, guild: Guild, invite_key: str, link: str
    ) -> InviteEntry:
        return self.guilds[guild.id].modify_invite_link(invite_key, link)

    # @implements InviteStore
    async def modify_invite_tags(
        self, guild: Guild, invite_key: str, tags: Tuple[str, ...]
    ) -> InviteEntry:
        return self.guilds[guild.id].modify_invite_tags(invite_key, tags)

    # @implements InviteStore
    async def modify_invite_description(
        self, guild: Guild, invite_key: str, description: Optional[str]
    ) -> InviteEntry:
        return self.guilds[guild.id].modify_invite_description(invite_key, description)

    # @implements InviteStore
    async def configure_guild_key(
        self, guild: Guild, invite_key: Optional[str]
    ) -> Optional[InviteEntry]:
        return self.guilds[guild.id].configure_guild_key(invite_key)
