from dataclasses import dataclass
from typing import Dict

from commanderbot_lib.types import GuildID


@dataclass
class FaqEntry:
    name: str
    content: str
    message_link: str

    @staticmethod
    async def deserialize(data: dict, name: str) -> "FaqEntry":
        if not isinstance(data, dict):
            raise ValueError(f"Invalid FAQ data: {type(data)}")
        content: str = data.get("content")
        if not isinstance(content, str):
            raise ValueError(f"Invalid FAQ content: {type(content)}")
        message_link = data.get("message_link")
        if not (message_link is None or isinstance(message_link, str)):
            raise ValueError(f"Invalid FAQ message link: {type(message_link)}")
        return FaqEntry(name=name, content=content, message_link=message_link)

    def serialize(self) -> dict:
        return {"content": self.content, "message_link": self.message_link}


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
