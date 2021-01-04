from datetime import datetime

from commanderbot_lib.database.abc.versioned_file_database import VersionedFileDatabase


async def m_1a_init_empty_aliases(database: VersionedFileDatabase, data: dict):
    now = datetime.utcnow().isoformat()
    for guild_id, guild_data in data["guilds"].items():
        for entry_key, entry_data in guild_data["entries"].items():
            entry_data["aliases"] = []
            entry_data["added_on"] = now
            entry_data["last_modified_on"] = now
            entry_data["hits"] = 0
