import sys
from datetime import datetime, timedelta
from importlib.metadata import version
from typing import Dict, Optional

from commanderbot_lib.bot.abc.commander_bot_base import CommanderBotBase
from discord.ext.commands import Bot


class StatusDetails:
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

        # Get python version.
        pyv = sys.version_info
        self.python_version: str = f"{pyv[0]}.{pyv[1]}.{pyv[2]}"

        # Get discord.py version.
        self.discord_py_version: str = version("discord.py")

        # Get commanderbot version, if available.
        self.commanderbot_version: Optional[str] = None
        try:
            self.commanderbot_version = version("commanderbot")
        except:
            pass

        # Get commanderbot-lib version.
        self.commanderbot_lib_version: str = version("commanderbot-lib")

        # Get commanderbot-ext version.
        self.commanderbot_ext_version: str = version("commanderbot-ext")

        # Get additional CommanderBot details, if available.
        self.started_at: Optional[datetime] = None
        self.connected_since: Optional[datetime] = None
        self.uptime: Optional[timedelta] = None
        if isinstance(self.bot, CommanderBotBase):
            self.started_at = self.bot.started_at
            self.connected_since = self.bot.connected_since
            self.uptime = self.bot.uptime

    @property
    def rows(self) -> Dict[str, str]:
        all_rows = {
            "python version": self.python_version,
            "discord.py version": self.discord_py_version,
            "commanderbot version": self.commanderbot_version,
            "commanderbot-lib version": self.commanderbot_lib_version,
            "commanderbot-ext version": self.commanderbot_ext_version,
            "started at": str(self.started_at) if self.started_at else None,
            "connected since": str(self.connected_since) if self.connected_since else None,
            "uptime": str(self.uptime) if self.uptime else None,
        }
        non_empty_rows = {k: v for k, v in all_rows.items() if v}
        return non_empty_rows

    @property
    def lines(self) -> str:
        rows = self.rows
        pad = 1 + max(len(key) for key in rows)
        lines = ("".join((f"{k}:".ljust(pad), "  ", v)) for k, v in rows.items())
        return lines
