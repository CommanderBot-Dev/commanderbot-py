from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

__all__ = (
    "DatabaseOptions",
    "InMemoryDatabaseOptions",
    "JsonFileDatabaseOptions",
    "SQLiteDatabaseOptions",
    "InvalidDatabaseOptions",
    "UnknownDatabaseType",
    "MissingDatabaseType",
    "UnsupportedDatabaseOptions",
    "make_database_options",
)


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


@dataclass
class SQLiteDatabaseOptions(DatabaseOptions):
    path: Optional[Path]
    no_init: Optional[bool] = None

    @staticmethod
    def from_dict(options: Dict[str, Any]) -> "SQLiteDatabaseOptions":
        return SQLiteDatabaseOptions(
            path=Path(options["path"]),
            no_init=options.get("no_init"),
        )

    @staticmethod
    def in_memory() -> "SQLiteDatabaseOptions":
        return SQLiteDatabaseOptions(path=None)


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
    """
    Create an instance of `DatabaseOptions` based on an arbitrary input object.
    """
    try:
        if not obj:
            return InMemoryDatabaseOptions()
        if isinstance(obj, str):
            # If it's a string, attempt to turn it into a path.
            try:
                path = Path(obj)
            except:
                pass
            else:
                # If it's also a valid path, use the file extension to determine which
                # type of database to use.
                if path.suffix == ".json":
                    return JsonFileDatabaseOptions(path=path)
                if path.suffix == ".sqlite":
                    return SQLiteDatabaseOptions(path=path)
        if isinstance(obj, dict):
            # If it's a dict, expect a `type` to be explicitly defined.
            db_type = obj.get("type")
            if not db_type:
                raise MissingDatabaseType(obj)
            if db_type == "in_memory":
                return InMemoryDatabaseOptions()
            if db_type == "json":
                return JsonFileDatabaseOptions.from_dict(obj)
            if db_type == "sqlite":
                return SQLiteDatabaseOptions.from_dict(obj)
            raise UnknownDatabaseType(obj, db_type)
    except Exception as ex:
        raise InvalidDatabaseOptions(obj) from ex
    raise InvalidDatabaseOptions(obj)
