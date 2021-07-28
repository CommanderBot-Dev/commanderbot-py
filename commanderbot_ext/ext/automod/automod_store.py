from typing import Any, AsyncIterable, Dict, Optional, Protocol

from discord import Guild

from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.ext.automod.automod_rule import AutomodRule
from commanderbot_ext.lib import JsonObject


class AutomodStore(Protocol):
    """
    Abstracts the data storage and persistence of the automod cog.
    """

    def all_rules(self, guild: Guild) -> AsyncIterable[AutomodRule]:
        ...

    def rules_for_event(
        self, guild: Guild, event: AutomodEvent
    ) -> AsyncIterable[AutomodRule]:
        ...

    def query_rules(self, guild: Guild, query: str) -> AsyncIterable[AutomodRule]:
        ...

    async def get_rule(self, guild: Guild, name: str) -> Optional[AutomodRule]:
        ...

    async def require_rule(self, guild: Guild, name: str) -> AutomodRule:
        ...

    async def serialize_rule(self, guild: Guild, name: str) -> Dict[str, Any]:
        ...

    async def add_rule(self, guild: Guild, data: JsonObject) -> AutomodRule:
        ...

    async def remove_rule(self, guild: Guild, name: str) -> AutomodRule:
        ...

    async def modify_rule(
        self, guild: Guild, name: str, data: JsonObject
    ) -> AutomodRule:
        ...

    async def increment_rule_hits(self, guild: Guild, name: str) -> AutomodRule:
        ...
