import re
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

from commanderbot_ext.ext.faq.faq_store import (
    FaqAliasUnavailable,
    FaqEntry,
    FaqKeyAlreadyExists,
    NoSuchFaq,
)
from commanderbot_ext.lib import GuildID, JsonObject
from commanderbot_ext.lib.utils import dict_without_falsies


# @implements FaqEntry
@dataclass
class FaqDataFaqEntry:
    key: str
    added_on: datetime
    modified_on: datetime
    hits: int
    content: str
    link: Optional[str]
    aliases: Set[str]
    tags: Set[str]

    @staticmethod
    def deserialize(data: JsonObject, key: str) -> "FaqDataFaqEntry":
        return FaqDataFaqEntry(
            key=key,
            added_on=datetime.fromisoformat(data["added_on"]),
            modified_on=datetime.fromisoformat(data["modified_on"]),
            hits=data["hits"],
            content=data["content"],
            link=data.get("link"),
            aliases=set(data.get("aliases", [])),
            tags=set(data.get("tags", [])),
        )

    def serialize(self) -> JsonObject:
        return {
            "added_on": self.added_on.isoformat(),
            "modified_on": self.modified_on.isoformat(),
            "hits": self.hits,
            "content": self.content,
            "link": self.link,
            "aliases": list(self.aliases),
            "tags": list(self.tags),
        }

    # @implements FaqEntry
    @property
    def sorted_aliases(self) -> List[str]:
        return sorted(self.aliases)

    # @implements FaqEntry
    @property
    def sorted_tags(self) -> List[str]:
        return sorted(self.tags)

    def update_modified_on(self) -> datetime:
        self.modified_on = datetime.utcnow()
        return self.modified_on


@dataclass
class FaqDataGuild:
    faq_entries: Dict[str, FaqDataFaqEntry] = field(default_factory=dict)
    prefix: Optional[str] = None
    match: Optional[re.Pattern] = None

    faq_entries_by_alias: Dict[str, FaqDataFaqEntry] = field(
        init=False, default_factory=dict
    )

    @staticmethod
    def deserialize(data: JsonObject) -> "FaqDataGuild":
        # Note that aliases will be constructed from entries, during post-init.
        raw_match = data.get("match")
        return FaqDataGuild(
            faq_entries={
                key: FaqDataFaqEntry.deserialize(raw_entry, key)
                for key, raw_entry in data.get("faq_entries", {}).items()
            },
            prefix=data.get("prefix"),
            match=re.compile(raw_match) if raw_match else None,
        )

    def __post_init__(self):
        # Build the list of aliases from entries.
        for entry in self.faq_entries.values():
            for alias in entry.aliases:
                self.faq_entries_by_alias[alias] = entry

    def _is_faq_key_available(self, faq_key: str) -> bool:
        # Check whether the given FAQ key (key or alias) is in either the FAQ map or
        # the alias map.
        return not (
            (faq_key in self.faq_entries) or (faq_key in self.faq_entries_by_alias)
        )

    def _get_tags_from_query(self, faq_query: str) -> Set[str]:
        return set(s[1:] for s in faq_query.split() if s.startswith("#"))

    def serialize(self) -> JsonObject:
        return dict_without_falsies(
            prefix=self.prefix,
            match=self.match.pattern if self.match else None,
            faq_entries={
                key: entry.serialize() for key, entry in self.faq_entries.items()
            },
        )

    def require_faq_entry(self, faq_key: str) -> FaqDataFaqEntry:
        # Return the FAQ entry, if it exists.
        if faq_entry := self.faq_entries.get(faq_key):
            return faq_entry
        # Otherwise, raise.
        raise NoSuchFaq(faq_key)

    def query_faq_entries(self, faq_query: str) -> Iterable[FaqDataFaqEntry]:
        # First, check for an exact match by key.
        if by_key := self.faq_entries.get(faq_query):
            yield by_key
        # Next, check for a match by alias.
        elif by_alias := self.faq_entries_by_alias.get(faq_query):
            yield by_alias
        # Next, check for any number of matches by tags.
        elif tags := self._get_tags_from_query(faq_query):
            # Yield FAQ entries that have *all* of the tags.
            for faq_entry in self.faq_entries.values():
                if tags.issubset(faq_entry.tags):
                    yield faq_entry

    def scan_for_faqs(self, text: str) -> Optional[List[FaqEntry]]:
        # First, if a prefix is configured, check if the text starts with it.
        if self.prefix and text.startswith(self.prefix):
            faq_query = text[len(self.prefix) :]
            return list(self.query_faq_entries(faq_query))
        # Next, if a match pattern is configured, look for matches in the text.
        elif self.match:
            if matches := self.match.findall(text):
                faq_entries = []
                for match in matches:
                    # Make sure not to introduce duplicates.
                    faq_entries_to_add = [
                        faq_entry
                        for faq_entry in self.query_faq_entries(match)
                        if faq_entry not in faq_entries
                    ]
                    faq_entries += faq_entries_to_add
                return faq_entries

    def add_faq(self, faq_key: str, link: str, content: str) -> FaqDataFaqEntry:
        # Ensure the given key is available.
        if not self._is_faq_key_available(faq_key):
            raise FaqKeyAlreadyExists(faq_key)
        # Create and register a new FAQ entry.
        now = datetime.utcnow()
        faq_entry = FaqDataFaqEntry(
            key=faq_key,
            added_on=now,
            modified_on=now,
            hits=0,
            content=content,
            link=link,
            aliases=set(),
            tags=set(),
        )
        self.faq_entries[faq_key] = faq_entry
        # Return the newly-created FAQ entry.
        return faq_entry

    def remove_faq(self, faq_key: str) -> FaqDataFaqEntry:
        # Remove and return the FAQ entry, if it exists.
        if faq_entry := self.faq_entries.pop(faq_key, None):
            # Make sure to also deregister all of its aliases.
            for alias in faq_entry.aliases:
                del self.faq_entries_by_alias[alias]
            # Return the FAQ entry.
            return faq_entry
        # Otherwise, if it does not exist, raise.
        raise NoSuchFaq(faq_key)

    def modify_faq_content(self, faq_key: str, content: str) -> FaqDataFaqEntry:
        if faq_entry := self.require_faq_entry(faq_key):
            faq_entry.update_modified_on()
            faq_entry.content = content
            return faq_entry
        raise NoSuchFaq(faq_key)

    def modify_faq_link(self, faq_key: str, link: Optional[str]) -> FaqDataFaqEntry:
        if faq_entry := self.require_faq_entry(faq_key):
            faq_entry.link = link
            return faq_entry
        raise NoSuchFaq(faq_key)

    def modify_faq_aliases(
        self, faq_key: str, aliases: Tuple[str, ...]
    ) -> FaqDataFaqEntry:
        if faq_entry := self.require_faq_entry(faq_key):
            requested_aliases = set(aliases)
            aliases_to_add = requested_aliases.difference(faq_entry.aliases)
            aliases_to_remove = faq_entry.aliases.difference(requested_aliases)
            # Ensure that each new alias is available.
            for alias_to_add in aliases_to_add:
                if not self._is_faq_key_available(alias_to_add):
                    raise FaqAliasUnavailable(alias_to_add)
            # Remove old aliases.
            for alias_to_remove in aliases_to_remove:
                faq_entry.aliases.remove(alias_to_remove)
                del self.faq_entries_by_alias[alias_to_remove]
            # Add new aliases.
            for alias_to_add in aliases_to_add:
                faq_entry.aliases.add(alias_to_add)
                self.faq_entries_by_alias[alias_to_add] = faq_entry
            # Return the FAQ entry.
            return faq_entry
        raise NoSuchFaq(faq_key)

    def modify_faq_tags(self, faq_key: str, tags: Tuple[str, ...]) -> FaqDataFaqEntry:
        if faq_entry := self.require_faq_entry(faq_key):
            faq_entry.tags = set(tags)
            return faq_entry
        raise NoSuchFaq(faq_key)

    def configure_prefix(self, prefix: Optional[str]):
        self.prefix = prefix

    def configure_match(self, match: Optional[str]):
        self.match = re.compile(match) if match else None


def _guilds_defaultdict_factory() -> DefaultDict[GuildID, FaqDataGuild]:
    return defaultdict(lambda: FaqDataGuild())


# @implements FaqStore
@dataclass
class FaqData:
    """
    Implementation of `FaqStore` using an in-memory object hierarchy.
    """

    guilds: DefaultDict[GuildID, FaqDataGuild] = field(
        default_factory=_guilds_defaultdict_factory
    )

    @staticmethod
    def deserialize(data: JsonObject) -> "FaqData":
        guilds = _guilds_defaultdict_factory()
        guilds.update(
            {
                int(guild_id): FaqDataGuild.deserialize(raw_guild_data)
                for guild_id, raw_guild_data in data.get("guilds", {}).items()
            }
        )
        return FaqData(guilds=guilds)

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

    # @implements FaqStore
    async def get_faq_entries(self, guild: Guild) -> List[FaqEntry]:
        return [faq_entry for faq_entry in self.guilds[guild.id].faq_entries.values()]

    # @implements FaqStore
    async def require_faq_entry(self, guild: Guild, faq_key: str) -> FaqEntry:
        return self.guilds[guild.id].require_faq_entry(faq_key)

    # @implements FaqStore
    async def query_faq_entries(
        self, guild: Guild, faq_query: str
    ) -> AsyncIterable[FaqEntry]:
        for faq_entry in self.guilds[guild.id].query_faq_entries(faq_query):
            yield faq_entry

    # @implements FaqStore
    async def scan_for_faqs(self, guild: Guild, text: str) -> Optional[List[FaqEntry]]:
        return self.guilds[guild.id].scan_for_faqs(text)

    # @implements FaqStore
    async def increment_faq_hits(self, faq_entry: FaqEntry):
        faq_entry.hits += 1

    # @implements FaqStore
    async def add_faq(
        self, guild: Guild, faq_key: str, link: str, content: str
    ) -> FaqEntry:
        return self.guilds[guild.id].add_faq(faq_key, link=link, content=content)

    # @implements FaqStore
    async def remove_faq(self, guild: Guild, faq_key: str) -> FaqEntry:
        return self.guilds[guild.id].remove_faq(faq_key)

    # @implements FaqStore
    async def modify_faq_content(
        self, guild: Guild, faq_key: str, content: str
    ) -> FaqEntry:
        return self.guilds[guild.id].modify_faq_content(faq_key, content)

    # @implements FaqStore
    async def modify_faq_link(
        self, guild: Guild, faq_key: str, link: Optional[str]
    ) -> FaqEntry:
        return self.guilds[guild.id].modify_faq_link(faq_key, link)

    # @implements FaqStore
    async def modify_faq_aliases(
        self, guild: Guild, faq_key: str, aliases: Tuple[str, ...]
    ) -> FaqEntry:
        return self.guilds[guild.id].modify_faq_aliases(faq_key, aliases)

    # @implements FaqStore
    async def modify_faq_tags(
        self, guild: Guild, faq_key: str, tags: Tuple[str, ...]
    ) -> FaqEntry:
        return self.guilds[guild.id].modify_faq_tags(faq_key, tags)

    # @implements FaqStore
    async def configure_prefix(self, guild: Guild, prefix: Optional[str]):
        self.guilds[guild.id].configure_prefix(prefix)

    # @implements FaqStore
    async def configure_match(self, guild: Guild, match: Optional[str]):
        self.guilds[guild.id].configure_match(match)
