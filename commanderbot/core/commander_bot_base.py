from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from discord.ext.commands import Bot

__all__ = ("CommanderBotBase",)


class CommanderBotBase(ABC, Bot):
    @property
    @abstractmethod
    def started_at(self) -> datetime:
        ...

    @property
    @abstractmethod
    def connected_since(self) -> datetime:
        ...

    @property
    @abstractmethod
    def uptime(self) -> timedelta:
        ...

    @abstractmethod
    def get_extension_options(self, ext_name: str) -> Optional[Dict[str, Any]]:
        ...
