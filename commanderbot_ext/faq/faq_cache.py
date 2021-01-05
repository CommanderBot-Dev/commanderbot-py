from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Set

from commanderbot_lib.types import GuildID


@dataclass
class FaqEntry:
    name: str
    content: str
    message_link: str
    aliases: Set[str]
    added_on: datetime
    last_modified_on: datetime
    hits: int

    @staticmethod
    async def deserialize(data: dict, name: str) -> "FaqEntry":
        if not isinstance(data, dict):
            raise ValueError(f"Invalid FAQ data: {type(data)}")

        # content
        content: str = data["content"]
        assert isinstance(content, str)

        # message_link
        message_link = data["message_link"]
        assert message_link is None or isinstance(message_link, str)

        # aliases
        aliases = data["aliases"]
        assert isinstance(aliases, list)
        for alias in aliases:
            assert isinstance(alias, str)

        # added_on
        raw_added_on = data["added_on"]
        assert isinstance(raw_added_on, str)
        added_on = datetime.fromisoformat(raw_added_on)

        # last_modified_on
        raw_last_modified_on = data["last_modified_on"]
        assert isinstance(raw_last_modified_on, str)
        last_modified_on = datetime.fromisoformat(raw_last_modified_on)

        # hits
        hits = data["hits"]
        assert isinstance(hits, int)

        return FaqEntry(
            name=name,
            content=content,
            message_link=message_link,
            aliases=set(aliases),
            added_on=added_on,
            last_modified_on=last_modified_on,
            hits=hits,
        )

    def serialize(self) -> dict:
        return {
            "content": self.content,
            "message_link": self.message_link,
            "aliases": list(self.aliases),
            "added_on": self.added_on.isoformat(),
            "last_modified_on": self.last_modified_on.isoformat(),
            "hits": self.hits,
        }


@dataclass
class FaqGuildData:
    guild_id: GuildID
    entries: Dict[str, FaqEntry]

    @staticmethod
    async def deserialize(data: dict, guild_id: GuildID) -> "FaqGuildData":
        if not isinstance(data, dict):
            raise ValueError(f"Invalid guild data: {type(data)}")
        raw_entries: dict = data.get("entries", {})
        if not isinstance(raw_entries, dict):
            raise ValueError(f"Invalid guild entries: {type(raw_entries)}")
        entries = {}
        for faq_name, raw_faq_entry in raw_entries.items():
            faq_entry = await FaqEntry.deserialize(raw_faq_entry, faq_name)
            entries[faq_name] = faq_entry
        return FaqGuildData(guild_id=guild_id, entries=entries)

    def serialize(self) -> dict:
        return {
            "entries": {
                faq_name: faq_entry.serialize() for faq_name, faq_entry in self.entries.items()
            }
        }


@dataclass
class FaqCache:
    guilds: Dict[GuildID, FaqGuildData]

    @staticmethod
    async def deserialize(data: dict) -> "FaqCache":
        if not isinstance(data, dict):
            raise ValueError(f"Invalid data: {type(data)}")
        raw_guilds: dict = data.get("guilds", {})
        if not isinstance(raw_guilds, dict):
            raise ValueError(f"Invalid guilds data: {type(raw_guilds)}")
        guilds = {}
        for raw_guild_id, raw_guild_data in raw_guilds.items():
            guild_id = int(raw_guild_id)
            guild_data = await FaqGuildData.deserialize(raw_guild_data, guild_id=guild_id)
            guilds[guild_id] = guild_data
        return FaqCache(guilds=guilds)

    def serialize(self) -> dict:
        return {
            "guilds": {
                guild_id: guild_data.serialize() for guild_id, guild_data in self.guilds.items()
            }
        }
