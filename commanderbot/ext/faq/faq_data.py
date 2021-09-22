import itertools
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import DefaultDict, Dict, Iterable, List, Optional, Set, Tuple

from discord import Guild

from commanderbot.ext.faq.faq_store import (
    FaqAliasUnavailable,
    FaqEntry,
    FaqKeyAlreadyExists,
    NoSuchFaq,
)
from commanderbot.lib import GuildID, JsonObject
from commanderbot.lib.utils import dict_without_falsies

TERM_SPLIT_PATTERN = re.compile(r"\W+")


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

    match_terms: Set[str] = field(init=False, default_factory=lambda: set())

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

    def __post_init__(self):
        self.sync()

    def __hash__(self) -> int:
        return hash(self.key)

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

    def _sync_match_terms(self):
        # Start wirth the key, all aliases, and all tags.
        terms = set((self.key, *self.aliases, *self.tags))
        # Also add all of the words from all of these things.
        for term in terms.copy():
            for word in TERM_SPLIT_PATTERN.split(term):
                terms.add(word)
        self.match_terms = terms

    def sync(self):
        self._sync_match_terms()

    def update_modified_on(self) -> datetime:
        self.modified_on = datetime.utcnow()
        return self.modified_on

    def matches_query(self, query: str) -> bool:
        query_terms = TERM_SPLIT_PATTERN.split(query)
        for term in query_terms:
            if term not in self.match_terms:
                return False
        return True


@dataclass
class FaqDataGuild:
    faq_entries: Dict[str, FaqDataFaqEntry] = field(default_factory=dict)
    prefix: Optional[re.Pattern] = None
    match: Optional[re.Pattern] = None

    faq_entries_by_alias: Dict[str, FaqDataFaqEntry] = field(
        init=False, default_factory=dict
    )

    @staticmethod
    def deserialize(data: JsonObject) -> "FaqDataGuild":
        # Note that aliases will be constructed from entries, during post-init.
        raw_prefix = data.get("prefix")
        raw_match = data.get("match")
        return FaqDataGuild(
            faq_entries={
                key: FaqDataFaqEntry.deserialize(raw_entry, key)
                for key, raw_entry in data.get("faq_entries", {}).items()
            },
            prefix=re.compile(raw_prefix) if raw_prefix else None,
            match=re.compile(raw_match) if raw_match else None,
        )

    def __post_init__(self):
        # Build the list of aliases from entries.
        for faq in self.faq_entries.values():
            for alias in faq.aliases:
                self.faq_entries_by_alias[alias] = faq

    def _is_faq_key_available(self, faq_key: str) -> bool:
        # Check whether the given FAQ key (key or alias) is in either the FAQ map or
        # the alias map.
        return not (
            (faq_key in self.faq_entries) or (faq_key in self.faq_entries_by_alias)
        )

    def serialize(self) -> JsonObject:
        return dict_without_falsies(
            prefix=self.prefix.pattern if self.prefix else None,
            match=self.match.pattern if self.match else None,
            faq_entries={
                key: entry.serialize() for key, entry in self.faq_entries.items()
            },
        )

    def get_prefix(self) -> Optional[re.Pattern]:
        return self.prefix

    def set_prefix(self, prefix: Optional[str]) -> Optional[re.Pattern]:
        self.prefix = re.compile(prefix) if prefix else None
        return self.prefix

    def get_match(self) -> Optional[re.Pattern]:
        return self.match

    def set_match(self, match: Optional[str]) -> Optional[re.Pattern]:
        self.match = re.compile(match) if match else None
        return self.match

    def get_faq(self, name: str) -> Optional[FaqDataFaqEntry]:
        # Return the FAQ entry by key, if it exists.
        if by_key := self.faq_entries.get(name):
            return by_key
        # Otherwise try to return it by alias.
        return self.faq_entries_by_alias.get(name)

    def require_faq(self, name: str) -> FaqDataFaqEntry:
        # Return the FAQ entry, if it exists.
        if faq := self.get_faq(name):
            return faq
        # Otherwise, raise.
        raise NoSuchFaq(name)

    def iter_faqs_by_query(self, query: str) -> Iterable[FaqDataFaqEntry]:
        # Yield FAQs that match the query.
        for faq in self.faq_entries.values():
            if faq.matches_query(query):
                yield faq

    def get_faqs_by_query(self, query: str, cap: int) -> List[FaqDataFaqEntry]:
        return list(itertools.islice(self.iter_faqs_by_query(query), cap))

    def iter_faqs_by_match(self, content: str) -> Iterable[FaqDataFaqEntry]:
        # If a match pattern is configured, look for matches in the text.
        if self.match:
            faqs = set()
            for match in self.match.finditer(content):
                query = "".join(match.groups())
                faq = self.get_faq(query)
                # Make sure not to introduce duplicates.
                if faq and (faq not in faqs):
                    faqs.add(faq)
                    yield faq

    def get_faqs_by_match(self, content: str, cap: int) -> List[FaqDataFaqEntry]:
        return list(itertools.islice(self.iter_faqs_by_match(content), cap))

    def add_faq(self, faq_key: str, link: str, content: str) -> FaqDataFaqEntry:
        # Ensure the given key is available.
        if not self._is_faq_key_available(faq_key):
            raise FaqKeyAlreadyExists(faq_key)
        # Create and register a new FAQ entry.
        now = datetime.utcnow()
        faq = FaqDataFaqEntry(
            key=faq_key,
            added_on=now,
            modified_on=now,
            hits=0,
            content=content,
            link=link,
            aliases=set(),
            tags=set(),
        )
        self.faq_entries[faq_key] = faq
        # Return the newly-created FAQ entry.
        return faq

    def remove_faq(self, name: str) -> FaqDataFaqEntry:
        # Expect the FAQ entry to exist.
        faq = self.require_faq(name)
        # Remove it.
        del self.faq_entries[faq.key]
        # Make sure to also deregister all of its aliases.
        for alias in faq.aliases:
            del self.faq_entries_by_alias[alias]
        # Return it.
        return faq

    def modify_faq_content(
        self, faq_key: str, link: str, content: str
    ) -> FaqDataFaqEntry:
        if faq := self.require_faq(faq_key):
            faq.update_modified_on()
            faq.content = content
            faq.link = link
            faq.sync()
            return faq
        raise NoSuchFaq(faq_key)

    def modify_faq_aliases(
        self, faq_key: str, aliases: Tuple[str, ...]
    ) -> FaqDataFaqEntry:
        if faq := self.require_faq(faq_key):
            requested_aliases = set(aliases)
            aliases_to_add = requested_aliases.difference(faq.aliases)
            aliases_to_remove = faq.aliases.difference(requested_aliases)

            # Ensure that each new alias is available.
            for alias_to_add in aliases_to_add:
                if not self._is_faq_key_available(alias_to_add):
                    raise FaqAliasUnavailable(alias_to_add)

            # Remove old aliases.
            for alias_to_remove in aliases_to_remove:
                faq.aliases.remove(alias_to_remove)
                del self.faq_entries_by_alias[alias_to_remove]

            # Add new aliases.
            for alias_to_add in aliases_to_add:
                faq.aliases.add(alias_to_add)
                self.faq_entries_by_alias[alias_to_add] = faq

            # Sync and return the FAQ entry.
            faq.sync()
            return faq

        raise NoSuchFaq(faq_key)

    def modify_faq_tags(self, faq_key: str, tags: Tuple[str, ...]) -> FaqDataFaqEntry:
        if faq := self.require_faq(faq_key):
            faq.tags = set(tags)
            faq.sync()
            return faq
        raise NoSuchFaq(faq_key)


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
    async def get_prefix_pattern(self, guild: Guild) -> Optional[re.Pattern]:
        return self.guilds[guild.id].get_prefix()

    # @implements FaqStore
    async def set_prefix_pattern(
        self, guild: Guild, prefix: Optional[str]
    ) -> Optional[re.Pattern]:
        return self.guilds[guild.id].set_prefix(prefix)

    # @implements FaqStore
    async def get_match_pattern(self, guild: Guild) -> Optional[re.Pattern]:
        return self.guilds[guild.id].get_match()

    # @implements FaqStore
    async def set_match_pattern(
        self, guild: Guild, match: Optional[str]
    ) -> Optional[re.Pattern]:
        return self.guilds[guild.id].set_match(match)

    # @implements FaqStore
    async def get_faq_by_name(self, guild: Guild, name: str) -> Optional[FaqEntry]:
        return self.guilds[guild.id].get_faq(name)

    # @implements FaqStore
    async def require_faq_by_name(self, guild: Guild, name: str) -> FaqEntry:
        return self.guilds[guild.id].require_faq(name)

    # @implements FaqStore
    async def get_all_faqs(self, guild: Guild) -> List[FaqEntry]:
        return list(self.guilds[guild.id].faq_entries.values())

    # @implements FaqStore
    async def get_faqs_by_query(
        self, guild: Guild, query: str, cap: int
    ) -> List[FaqEntry]:
        return self.guilds[guild.id].get_faqs_by_query(query, cap)

    # @implements FaqStore
    async def get_faqs_by_match(
        self, guild: Guild, content: str, cap: int
    ) -> List[FaqEntry]:
        return self.guilds[guild.id].get_faqs_by_match(content, cap)

    # @implements FaqStore
    async def increment_faq_hits(self, faq: FaqEntry):
        faq.hits += 1

    # @implements FaqStore
    async def add_faq(
        self, guild: Guild, key: str, link: str, content: str
    ) -> FaqEntry:
        return self.guilds[guild.id].add_faq(key, link=link, content=content)

    # @implements FaqStore
    async def remove_faq(self, guild: Guild, name: str) -> FaqEntry:
        return self.guilds[guild.id].remove_faq(name)

    # @implements FaqStore
    async def modify_faq_content(
        self, guild: Guild, name: str, link: str, content: str
    ) -> FaqEntry:
        return self.guilds[guild.id].modify_faq_content(
            name, link=link, content=content
        )

    # @implements FaqStore
    async def modify_faq_aliases(
        self, guild: Guild, name: str, aliases: Tuple[str, ...]
    ) -> FaqEntry:
        return self.guilds[guild.id].modify_faq_aliases(name, aliases)

    # @implements FaqStore
    async def modify_faq_tags(
        self, guild: Guild, name: str, tags: Tuple[str, ...]
    ) -> FaqEntry:
        return self.guilds[guild.id].modify_faq_tags(name, tags)
