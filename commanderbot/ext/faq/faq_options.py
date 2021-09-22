from dataclasses import dataclass, field
from typing import Any, Dict

from commanderbot.lib import (
    DatabaseOptions,
    InMemoryDatabaseOptions,
    make_database_options,
)


@dataclass
class FaqOptions:
    database: DatabaseOptions = field(default_factory=InMemoryDatabaseOptions)

    allow_prefix: bool = True
    allow_match: bool = True
    match_cap: int = 3
    query_cap: int = 10

    @staticmethod
    def from_dict(options: Dict[str, Any]) -> "FaqOptions":
        database_options = make_database_options(options.get("database"))
        return FaqOptions(
            database=database_options,
            allow_prefix=options.get("allow_prefix", True),
            allow_match=options.get("allow_match", True),
            match_cap=options.get("match_cap", 3),
            query_cap=options.get("query_cap", 10),
        )
