from typing import Any, Optional

from discord import Object
from discord.ext.commands import Cog

from commanderbot.lib.responsive_exception import ResponsiveException


class SudoException(ResponsiveException):
    pass


class SyncError(SudoException):
    def __init__(self, guild: Object, reason: str):
        super().__init__(
            f"**Unable to sync app commands to this guild:**\n"
            f"Guild ID: `{guild.id}`\n"
            f"Reason: `{reason}`"
        )


class SyncUnknownGuild(SudoException):
    def __init__(self, guild: Optional[Object]):
        super().__init__(f"**Unknown guild:**\nGuild ID: `{guild.id}`" if guild else "")


class UnknownCog(SudoException):
    def __init__(self, cog: str):
        super().__init__(f"Unable to find a loaded cog with the name `{cog}`")


class CogHasNoStore(SudoException):
    def __init__(self, cog: Cog):
        super().__init__(f"The cog `{cog.qualified_name}` does not use a store")


class UnsupportedStoreExport(SudoException):
    def __init__(self, store: Any):
        super().__init__(f"Unsupported store export: `{type(store)}`")
