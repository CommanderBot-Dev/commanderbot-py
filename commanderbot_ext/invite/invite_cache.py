from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Set, Tuple

from discord import Message

from commanderbot_lib.types import GuildID


@dataclass
class InviteEntry:
    name: str
    link: str
    tags: Set[str]
    added_on: datetime
    updated_on: datetime
    hits: int

    @staticmethod
    async def deserialize(data: dict, name: str) -> "InviteEntry":
        if not isinstance(data, dict):
            raise ValueError(f"Invalid INVITE data: {type(data)}")

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

        # updated_on
        raw_updated_on = data["updated_on"]
        assert isinstance(raw_updated_on, str)
        updated_on = datetime.fromisoformat(raw_updated_on)

        # hits
        hits = data["hits"]
        assert isinstance(hits, int)

        return InviteEntry(
            name=name,
            content=content,
            message_link=message_link,
            aliases=set(aliases),
            added_on=added_on,
            updated_on=updated_on,
            hits=hits,
        )

    def serialize(self) -> dict:
        return {
            "content": self.content,
            "message_link": self.message_link,
            "aliases": list(self.aliases),
            "added_on": self.added_on.isoformat(),
            "updated_on": self.updated_on.isoformat(),
            "hits": self.hits,
        }


@dataclass
class InviteGuildData:
    guild_id: GuildID
    entries: Dict[str, InviteEntry]
    aliases: Dict[str, InviteEntry]
    confirmation: Dict[int, Tuple[Message, InviteEntry]]

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
        aliases = {}
        for _, entry in entries.items():
            for alias in entry.aliases:
                aliases[alias] = entry
        return InviteGuildData(
            guild_id=guild_id, entries=entries, aliases=aliases, confirmation={}
        )

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
