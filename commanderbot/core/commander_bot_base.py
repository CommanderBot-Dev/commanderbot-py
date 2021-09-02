from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Callable, Coroutine, Dict, Optional, TypeAlias

from discord.ext.commands import Bot, Context

from commanderbot.lib.event_data import EventData

EventErrorHandler: TypeAlias = Callable[
    [Exception, EventData, bool], Coroutine[Any, Any, Optional[bool]]
]

CommandErrorHandler: TypeAlias = Callable[
    [Exception, Context, bool], Coroutine[Any, Any, Optional[bool]]
]


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

    @abstractmethod
    def add_event_error_handler(self, handler: EventErrorHandler):
        ...

    @abstractmethod
    def add_command_error_handler(self, handler: CommandErrorHandler):
        ...
