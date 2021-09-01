import re
import sys
from datetime import datetime, timedelta, timezone
from importlib.metadata import version
from typing import Dict, Optional

from discord.ext.commands import Bot

from commanderbot.core.utils import check_commander_bot


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

        # Get additional bot details, if available.
        self.started_at: Optional[datetime] = None
        self.last_reconnect: Optional[datetime] = None
        self.uptime: Optional[timedelta] = None
        if cb := check_commander_bot(bot):
            self.started_at = cb.started_at
            self.last_reconnect = cb.connected_since
            self.uptime = cb.uptime

    def _get_epoch(self, dt: Optional[datetime]) -> Optional[int]:
        if dt:
            return int(dt.replace(tzinfo=timezone.utc).timestamp())
        else:
            return None

    def _format_timedelta(self, td: Optional[timedelta]) -> Optional[str]:
        if not td:
            return None

        times = [int(float(i)) for i in re.split("days?,|:", str(td))]
        if len(times) == 4:
            return f"{times[0]}d {times[1]}h {times[2]}m {times[3]}s"
        else:
            return f"0d {times[0]}h {times[1]}m {times[2]}s"

    @property
    def rows(self) -> Dict[str, str]:
        all_rows = {
            "Python version": f"`{self.python_version}`",
            "Discord.py version": f"`{self.discord_py_version}`",
            "CommanderBot version": f"`{self.commanderbot_version}`",
            "Started": f"<t:{self._get_epoch(self.started_at)}:R>",
            "Last reconnect": f"<t:{self._get_epoch(self.last_reconnect)}:R>",
            "Uptime": f"`{self._format_timedelta(self.uptime)}`",
        }
        non_empty_rows = {k: v for k, v in all_rows.items() if v}
        return non_empty_rows
