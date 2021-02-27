from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

from commanderbot_lib.types import GuildID, IDType
from discord import Client, TextChannel
from discord.ext.commands import Context


@dataclass
class HelpChannel:
    channel_id: IDType
    registered_on: datetime

    @staticmethod
    async def deserialize(data: dict) -> "HelpChannel":
        if not isinstance(data, dict):
            raise ValueError(f"Invalid help channel: {type(data)}")

        # channel_id
        channel_id: int = data["channel_id"]
        assert isinstance(channel_id, int)

        # registered_on
        raw_registered_on: str = data["registered_on"]
        assert isinstance(raw_registered_on, str)
        registered_on: datetime = datetime.fromisoformat(raw_registered_on)

        return HelpChannel(
            channel_id=channel_id,
            registered_on=registered_on,
        )

    def serialize(self) -> dict:
        return {
            "channel_id": self.channel_id,
            "registered_on": self.registered_on.isoformat(),
        }

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


DEFAULT_REPORT_SPLIT_LENGTH = 1000
DEFAULT_REPORT_MAX_ROWS = 50
DEFAULT_REPORT_MIN_SCORE = 1


@dataclass
class HelpChatGuildData:
    guild_id: GuildID
    help_channels: List[HelpChannel] = field(default_factory=list)
    default_report_split_length: int = DEFAULT_REPORT_SPLIT_LENGTH
    default_report_max_rows: int = DEFAULT_REPORT_MAX_ROWS
    default_report_min_score: int = DEFAULT_REPORT_MIN_SCORE

    @staticmethod
    async def deserialize(data: dict, guild_id: GuildID) -> "HelpChatGuildData":
        if not isinstance(data, dict):
            raise ValueError(f"Invalid guild data: {type(data)}")

        # help_channels
        raw_help_channels: list = data.get("help_channels", [])
        if not isinstance(raw_help_channels, list):
            raise ValueError(f"Invalid guild help channels: {type(raw_help_channels)}")
        help_channels = []
        for raw_help_channel in raw_help_channels:
            help_channel = await HelpChannel.deserialize(raw_help_channel)
            help_channels.append(help_channel)

        return HelpChatGuildData(
            guild_id=guild_id,
            help_channels=help_channels,
            default_report_split_length=data.get("default_report_split_length"),
            default_report_max_rows=data.get("default_report_max_rows"),
            default_report_min_score=data.get("default_report_min_score"),
        )

    def serialize(self) -> dict:
        return {
            "help_channels": [
                help_channel.serialize() for help_channel in self.help_channels
            ],
            "default_report_split_length": self.default_report_split_length,
            "default_report_max_rows": self.default_report_max_rows,
            "default_report_min_score": self.default_report_min_score,
        }


@dataclass
class HelpChatCache:
    guilds: Dict[GuildID, HelpChatGuildData]

    @staticmethod
    async def deserialize(data: dict) -> "HelpChatCache":
        if not isinstance(data, dict):
            raise ValueError(f"Invalid data: {type(data)}")
        raw_guilds: dict = data.get("guilds", {})
        if not isinstance(raw_guilds, dict):
            raise ValueError(f"Invalid guilds data: {type(raw_guilds)}")
        guilds = {}
        for raw_guild_id, raw_guild_data in raw_guilds.items():
            guild_id = int(raw_guild_id)
            guild_data = await HelpChatGuildData.deserialize(
                raw_guild_data, guild_id=guild_id
            )
            guilds[guild_id] = guild_data
        return HelpChatCache(guilds=guilds)

    def serialize(self) -> dict:
        return {
            "guilds": {
                guild_id: guild_data.serialize()
                for guild_id, guild_data in self.guilds.items()
            }
        }
