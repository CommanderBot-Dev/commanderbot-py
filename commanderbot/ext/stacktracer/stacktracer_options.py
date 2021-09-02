from dataclasses import dataclass, field
from typing import Any, Optional, Type, TypeVar

from commanderbot.lib import (
    DatabaseOptions,
    FromDataMixin,
    InMemoryDatabaseOptions,
    make_database_options,
)

ST = TypeVar("ST")


@dataclass
class StacktracerOptions(FromDataMixin):
    database: DatabaseOptions = field(default_factory=InMemoryDatabaseOptions)

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, dict):
            database_options = make_database_options(data.get("database"))
            return cls(database=database_options)
