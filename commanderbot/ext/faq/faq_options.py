from dataclasses import dataclass, field
from typing import Any, Dict

from commanderbot_ext.lib import (
    DatabaseOptions,
    InMemoryDatabaseOptions,
    make_database_options,
)


@dataclass
class FaqOptions:
    database: DatabaseOptions = field(default_factory=InMemoryDatabaseOptions)

    @staticmethod
    def from_dict(options: Dict[str, Any]) -> "FaqOptions":
        database_options = make_database_options(options.get("database"))
        return FaqOptions(database=database_options)
