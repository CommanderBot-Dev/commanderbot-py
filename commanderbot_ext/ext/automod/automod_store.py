from typing import AsyncIterable, Optional, Protocol, Tuple

from discord import Guild, TextChannel

from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.ext.automod.automod_log_options import AutomodLogOptions
from commanderbot_ext.ext.automod.automod_rule import AutomodRule
from commanderbot_ext.lib import JsonObject


class AutomodStore(Protocol):
    """
    Abstracts the data storage and persistence of the automod cog.
    """

    async def get_default_log_options(
        self, guild: Guild
    ) -> Optional[AutomodLogOptions]:
        ...

    async def set_default_log_options(
        self, guild: Guild, log_options: Optional[AutomodLogOptions]
    ) -> Optional[AutomodLogOptions]:
        ...

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

    async def add_rule(self, guild: Guild, data: JsonObject) -> AutomodRule:
        ...

    async def remove_rule(self, guild: Guild, name: str) -> AutomodRule:
        ...

    async def modify_rule(
        self, guild: Guild, name: str, data: JsonObject
    ) -> AutomodRule:
        ...

    async def enable_rule(self, guild: Guild, name: str) -> AutomodRule:
        ...

    async def disable_rule(self, guild: Guild, name: str) -> AutomodRule:
        ...

    async def increment_rule_hits(self, guild: Guild, name: str) -> AutomodRule:
        ...
