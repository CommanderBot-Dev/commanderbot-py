from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DatabaseOptions:
    pass


@dataclass
class InMemoryDatabaseOptions(DatabaseOptions):
    pass


@dataclass
class JsonFileDatabaseOptions(DatabaseOptions):
    path: Path
    auto_create: bool = True


class InvalidDatabaseOptions(Exception):
    def __init__(self, raw_options: Any):
        self.raw_options = raw_options
        super().__init__(f"Invalid database options: {raw_options}")


class UnsupportedDatabaseOptions(Exception):
    def __init__(self, database_options: DatabaseOptions):
        self.database_options = database_options
        super().__init__(f"Unsupported database options: {database_options}")


def make_database_options(raw_database_options: Any) -> DatabaseOptions:
    if not raw_database_options:
        return InMemoryDatabaseOptions()
    if isinstance(raw_database_options, str):
        if raw_database_options.endswith(".json"):
            return JsonFileDatabaseOptions(path=Path(raw_database_options))
    raise InvalidDatabaseOptions(raw_database_options)
