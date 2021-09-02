from typing import Optional, Protocol

from discord import Guild

from commanderbot.lib.log_options import LogOptions


class StacktracerStore(Protocol):
    """
    Abstracts the data storage and persistence of the Stacktracer cog.
    """

    async def get_global_log_options(self) -> Optional[LogOptions]:
        ...

    async def set_global_log_options(
        self, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        ...

    async def get_guild_log_options(self, guild: Guild) -> Optional[LogOptions]:
        ...

    async def set_guild_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        ...
