from dataclasses import dataclass, field
from typing import Any, Dict

from commanderbot.lib import (
    DatabaseOptions,
    InMemoryDatabaseOptions,
    make_database_options,
)


@dataclass
class InviteOptions:
    database: DatabaseOptions = field(default_factory=InMemoryDatabaseOptions)

    @staticmethod
    def from_dict(options: Dict[str, Any]) -> "InviteOptions":
        database_options = make_database_options(options.get("database"))
        return InviteOptions(database=database_options)
