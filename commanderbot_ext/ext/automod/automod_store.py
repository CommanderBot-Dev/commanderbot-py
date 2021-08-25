from typing import AsyncIterable, Optional, Protocol

from discord import Guild, Member

from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.ext.automod.automod_log_options import AutomodLogOptions
from commanderbot_ext.ext.automod.automod_rule import AutomodRule
from commanderbot_ext.lib import JsonObject, RoleSet


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

    async def get_permitted_roles(self, guild: Guild) -> Optional[RoleSet]:
        ...

    async def set_permitted_roles(
        self, guild: Guild, permitted_roles: Optional[RoleSet]
    ) -> Optional[RoleSet]:
        ...

    async def member_has_permission(self, guild: Guild, member: Member) -> bool:
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
