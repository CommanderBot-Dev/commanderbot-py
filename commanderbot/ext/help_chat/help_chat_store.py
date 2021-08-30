from datetime import datetime
from typing import List, Optional, Protocol

from discord import Guild, TextChannel
from discord.ext.commands import Context

from commanderbot_ext.lib import ChannelID


class HelpChannel(Protocol):
    channel_id: ChannelID
    registered_on: datetime

    def channel(self, ctx: Context) -> TextChannel:
        ...


class HelpChatStore(Protocol):
    """
    Abstracts the data storage and persistence of the help-chat cog.
    """

    async def get_help_channels(self, guild: Guild) -> List[HelpChannel]:
        ...

    async def get_help_channel(
        self, guild: Guild, channel: TextChannel
    ) -> Optional[HelpChannel]:
        ...

    async def add_help_channel(self, guild: Guild, channel: TextChannel) -> HelpChannel:
        ...

    async def remove_help_channel(
        self, guild: Guild, channel: TextChannel
    ) -> HelpChannel:
        ...
