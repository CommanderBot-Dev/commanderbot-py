from dataclasses import dataclass
from typing import List, Optional, cast

from discord import Guild, TextChannel
from sqlalchemy.future import select
from sqlalchemy.sql.expression import insert

from commanderbot_ext.ext.help_chat.help_chat_store import HelpChannel
from commanderbot_ext.ext.help_chat.sql_store import models
from commanderbot_ext.lib import CogStore, SQLDatabaseAdapter

__all__ = ("HelpChatSQLStore",)


# @implements HelpChatStore
@dataclass
class HelpChatSQLStore(CogStore):
    """
    Implementation of `HelpChatStore` that uses a SQL database to persist state.
    """

    db: SQLDatabaseAdapter

    async def _ensure_init(self):
        async with self.db.connect() as conn:
            await conn.run_sync(models.metadata.create_all)

    async def get_help_channels(self, guild: Guild) -> List[HelpChannel]:
        await self._ensure_init()
        async with self.db.session() as session:
            result = await session.execute(
                select(models.HelpChannel).where(
                    models.HelpChannel.guild_id == guild.id
                )
            )
            rows = result.all()
        help_channels = [row[0] for row in rows]
        return cast(List[models.HelpChannel], help_channels)

    async def get_help_channel(
        self, guild: Guild, channel: TextChannel
    ) -> Optional[HelpChannel]:
        await self._ensure_init()
        async with self.db.session() as session:
            help_channel = await session.get(
                models.HelpChannel, {"guild_id": guild.id, "channel_id": channel.id}
            )
        return cast(Optional[models.HelpChannel], help_channel)

    async def add_help_channel(self, guild: Guild, channel: TextChannel) -> HelpChannel:
        await self._ensure_init()
        async with self.db.session() as session:
            # insert row
            await session.execute(
                insert(
                    models.HelpChannel,
                    [{"guild_id": guild.id, "channel_id": channel.id}],
                )
            )
            # commit
            await session.commit()
            # get row back
            help_channel = await session.get(
                models.HelpChannel, {"guild_id": guild.id, "channel_id": channel.id}
            )
        assert isinstance(help_channel, models.HelpChannel)
        return help_channel

    async def remove_help_channel(
        self, guild: Guild, channel: TextChannel
    ) -> HelpChannel:
        await self._ensure_init()
        async with self.db.session() as session:
            # get row
            help_channel = await session.get(
                models.HelpChannel, {"guild_id": guild.id, "channel_id": channel.id}
            )
            # delete row
            await session.delete(help_channel)
            # commit
            await session.commit()
        assert isinstance(help_channel, models.HelpChannel)
        return help_channel
