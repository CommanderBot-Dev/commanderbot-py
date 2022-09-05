from typing import Optional

from discord import Object

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
        super().__init__(
            f"**Unknown guild:**\n"
            f"Guild ID: `{guild.id}`" if guild else ""
        )
