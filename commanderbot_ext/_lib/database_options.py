from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class DatabaseOptions:
    pass


@dataclass
class InMemoryDatabaseOptions(DatabaseOptions):
    pass


@dataclass
class JsonFileDatabaseOptions(DatabaseOptions):
    path: Path
    no_init: Optional[bool] = None
    indent: Optional[int] = None

    @staticmethod
    def from_dict(options: Dict[str, Any]) -> "JsonFileDatabaseOptions":
        return JsonFileDatabaseOptions(
            path=Path(options["path"]),
            no_init=options.get("no_init"),
            indent=options.get("indent"),
        )


class InvalidDatabaseOptions(Exception):
    def __init__(self, raw_options: Any):
        self.raw_options = raw_options
        super().__init__(f"Invalid database options: {raw_options}")


class UnknownDatabaseType(Exception):
    def __init__(self, raw_options: Any, db_type: str):
        self.raw_options = raw_options
        self.db_type = db_type
        super().__init__(f'Unknown database type "{db_type}" in options: {raw_options}')


class MissingDatabaseType(Exception):
    def __init__(self, raw_options: Any):
        self.raw_options = raw_options
        super().__init__(f"Missing database type in options: {raw_options}")


class UnsupportedDatabaseOptions(Exception):
    def __init__(self, database_options: DatabaseOptions):
        self.database_options = database_options
        super().__init__(f"Unsupported database options: {database_options}")


def make_database_options(obj: Any) -> DatabaseOptions:
    try:
        if not obj:
            return InMemoryDatabaseOptions()
        if isinstance(obj, str):
            if obj.endswith(".json"):
                return JsonFileDatabaseOptions(path=Path(obj))
        if isinstance(obj, dict):
            db_type = obj.get("type")
            if db_type == "json":
                return JsonFileDatabaseOptions.from_dict(obj)
            elif db_type:
                raise UnknownDatabaseType(obj, db_type)
            else:
                raise MissingDatabaseType(obj)
    except Exception as ex:
        raise InvalidDatabaseOptions(obj) from ex
    raise InvalidDatabaseOptions(obj)
