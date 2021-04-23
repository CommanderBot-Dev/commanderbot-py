import sys
from datetime import datetime, timedelta
from importlib.metadata import version
from typing import Dict, Iterable, Optional

from discord.ext.commands import Bot

from commanderbot_ext.lib.utils import check_commander_bot


class StatusDetails:
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

        # Get python version.
        pyv = sys.version_info
        self.python_version: str = f"{pyv[0]}.{pyv[1]}.{pyv[2]}"

        # Get discord.py version.
        self.discord_py_version: str = version("discord.py")

        # Get commanderbot version.
        self.commanderbot_version: str = version("commanderbot")

        # Get commanderbot-ext version.
        self.commanderbot_ext_version: str = version("commanderbot-ext")

        # Get additional bot details, if available.
        self.started_at: Optional[datetime] = None
        self.connected_since: Optional[datetime] = None
        self.uptime: Optional[timedelta] = None
        if cb := check_commander_bot(bot):
            self.started_at = cb.started_at
            self.connected_since = cb.connected_since
            self.uptime = cb.uptime

    @property
    def rows(self) -> Dict[str, str]:
        all_rows = {
            "python version": self.python_version,
            "discord.py version": self.discord_py_version,
            "commanderbot version": self.commanderbot_version,
            "commanderbot-ext version": self.commanderbot_ext_version,
            "started at": str(self.started_at) if self.started_at else None,
            "connected since": str(self.connected_since)
            if self.connected_since
            else None,
            "uptime": str(self.uptime) if self.uptime else None,
        }
        non_empty_rows = {k: v for k, v in all_rows.items() if v}
        return non_empty_rows

    @property
    def lines(self) -> Iterable[str]:
        rows = self.rows
        pad = 1 + max(len(key) for key in rows)
        lines = ("".join((f"{k}:".ljust(pad), "  ", v)) for k, v in rows.items())
        return lines
