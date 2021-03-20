from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Set, Tuple, List

from discord import Message

from commanderbot_lib.types import GuildID


@dataclass
class InviteEntry:
    name: str
    link: str
    tags: Set[str]
    hits: int
    added_on: datetime

    @staticmethod
    async def deserialize(data: dict, name: str) -> "InviteEntry":
        if not isinstance(data, dict):
            raise ValueError(f"Invalid INVITE data: {type(data)}")

        # link
        link: str = data["link"]
        assert isinstance(link, str)

        # tags
        tags = data["tags"]
        assert isinstance(tags, list)
        for tag in tags:
            assert isinstance(tag, str)

        # hits
        hits = data["hits"]
        assert isinstance(hits, int)

        # added_on
        raw_added_on = data["added_on"]
        assert isinstance(raw_added_on, str)
        added_on = datetime.fromisoformat(raw_added_on)

        return InviteEntry(name=name, link=link, tags=set(tags), hits=hits, added_on=added_on)

    def serialize(self) -> dict:
        return {"link": self.link, "tags": list(self.tags), "hits": self.hits, "added_on": self.added_on.isoformat()}


@dataclass
class InviteGuildData:
    guild_id: GuildID
    entries: Dict[str, InviteEntry]
    tags: Dict[str, List[InviteEntry]]

    @staticmethod
    async def deserialize(data: dict, guild_id: GuildID) -> "InviteGuildData":
        if not isinstance(data, dict):
            raise ValueError(f"Invalid guild data: {type(data)}")
        raw_entries: dict = data.get("entries", {})
        if not isinstance(raw_entries, dict):
            raise ValueError(f"Invalid guild entries: {type(raw_entries)}")
        entries = {}
        for invite_name, raw_invite_entry in raw_entries.items():
            invite_entry = await InviteEntry.deserialize(raw_invite_entry, invite_name)
            entries[invite_name] = invite_entry
        tags = {}
        for _, entry in entries.items():
            for tag in entry.tags:
                if tag not in tags:
                    tags[tag] = []
                tags[tag].append(entry)
        return InviteGuildData(guild_id=guild_id, entries=entries, tags=tags)

    def serialize(self) -> dict:
        return {
            "entries": {
                invite_name: invite_entry.serialize()
                for invite_name, invite_entry in self.entries.items()
            }
        }


@dataclass
class InviteCache:
    guilds: Dict[GuildID, InviteGuildData]

    @staticmethod
    async def deserialize(data: dict) -> "InviteCache":
        if not isinstance(data, dict):
            raise ValueError(f"Invalid data: {type(data)}")
        raw_guilds: dict = data.get("guilds", {})
        if not isinstance(raw_guilds, dict):
            raise ValueError(f"Invalid guilds data: {type(raw_guilds)}")
        guilds = {}
        for raw_guild_id, raw_guild_data in raw_guilds.items():
            guild_id = int(raw_guild_id)
            guild_data = await InviteGuildData.deserialize(
                raw_guild_data, guild_id=guild_id
            )
            guilds[guild_id] = guild_data
        return InviteCache(guilds=guilds)

    def serialize(self) -> dict:
        return {
            "guilds": {
                guild_id: guild_data.serialize()
                for guild_id, guild_data in self.guilds.items()
            }
        }

    def add_guild(self, guild_id: GuildID):
        self.guilds[guild_id] = InviteGuildData(guild_id=guild_id, entries={}, tags={})
