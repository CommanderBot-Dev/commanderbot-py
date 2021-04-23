from dataclasses import dataclass, field
from logging import Logger, getLogger
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncConnection

from commanderbot_ext.lib.database_options import SQLiteDatabaseOptions

__all__ = ("SQLiteDatabaseAdapter",)


@dataclass
class SQLiteDatabaseAdapter:
    """
    Wraps common operations for persistent data backed by a SQLite database.

    Attributes
    ----------
    options
        Immutable, pre-defined settings that define core database behaviour.
    log
        A logger named in a uniquely identifiable way.
    engine
        The underlying SQLAlchemy engine object.
    """

    options: SQLiteDatabaseOptions

    log: Logger = field(init=False)
    engine: AsyncEngine = field(init=False)

    @property
    def path_or_in_memory(self) -> Optional[Path]:
        return self.options.path

    def __post_init__(self):
        if path := self.path_or_in_memory:
            self.log = getLogger(f"{path.name} ({self.__class__.__name__}#{id(self)})")
            self.log.info(f"Creating SQLite engine at: {path}")
            path_str = f"sqlite+aiosqlite:///{path}"
        else:
            self.log = getLogger(f"IN-MEMORY ({self.__class__.__name__}#{id(self)})")
            self.log.info("Creating IN-MEMORY SQLite engine")
            path_str = "sqlite://"
        self.engine = create_async_engine(path_str)

    def connect(self) -> AsyncConnection:
        return self.engine.connect()

    def begin(self) -> AsyncConnection:
        return self.engine.begin()

    def session(self) -> AsyncSession:
        return AsyncSession(self.engine)
