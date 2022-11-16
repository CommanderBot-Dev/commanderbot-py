from enum import Enum, auto
from typing import Protocol, Union, runtime_checkable

from commanderbot.lib import (
    JsonFileDatabaseAdapter,
    SQLDatabaseAdapter,
    SQLiteDatabaseAdapter,
)


@runtime_checkable
class DatabaseAdapter(Protocol):
    db: Union[JsonFileDatabaseAdapter, SQLiteDatabaseAdapter, SQLDatabaseAdapter]


@runtime_checkable
class CogUsesStore(Protocol):
    store: DatabaseAdapter


class SyncType(Enum):
    SYNC_ONLY = auto()
    COPY = auto()
    REMOVE = auto()
