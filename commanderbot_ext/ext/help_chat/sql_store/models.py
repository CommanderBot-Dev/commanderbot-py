from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

from discord import TextChannel
from discord.ext.commands import Context
from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.orm.decl_api import registry

mapper_registry = registry()
metadata = mapper_registry.metadata
sqmetakey = "sqmeta"


def sqmeta(meta: Any) -> Dict[str, Any]:
    return {sqmetakey: meta}


class Base:
    __sa_dataclass_metadata_key__ = sqmetakey


@mapper_registry.mapped
@dataclass
class HelpChannel(Base):
    __tablename__ = "help_channel"

    # The ID of the corresponding Discord guild.
    guild_id: int = field(
        init=False,
        metadata=sqmeta(Column(Integer, primary_key=True, autoincrement=False)),
    )

    # The ID of the corresponding Discord channel.
    channel_id: int = field(
        init=False,
        metadata=sqmeta(Column(Integer, primary_key=True, autoincrement=False)),
    )

    # The date the corresponding Discord channel was registered as a help channel.
    registered_on: datetime = field(
        init=False, metadata=sqmeta(Column(DateTime, server_default=func.now()))
    )

    # (Required for `server_default` attributes.)
    __mapper_args__ = {"eager_defaults": True}

    def channel(self, ctx: Context) -> TextChannel:
        channel = ctx.bot.get_channel(self.channel_id)
        if channel is None:
            raise ValueError(
                f"Failed to resolve help channel from channel ID: {self.channel}"
            )
        if not isinstance(channel, TextChannel):
            raise ValueError(
                f"Help channel resolved into non-text type channel: {channel}"
            )
        return channel
