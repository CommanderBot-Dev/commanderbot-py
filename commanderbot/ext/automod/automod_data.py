from asyncio.locks import Condition
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, AsyncIterable, DefaultDict, Dict, Optional, Type, TypeVar, cast

from discord import Guild

from commanderbot.ext.automod.action import Action, ActionCollection
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.bucket import Bucket, BucketCollection
from commanderbot.ext.automod.condition import Condition, ConditionCollection
from commanderbot.ext.automod.node import Node, NodeCollection
from commanderbot.ext.automod.rule import Rule, RuleCollection
from commanderbot.ext.automod.trigger import Trigger, TriggerCollection
from commanderbot.lib import FromData, GuildID, LogOptions, RoleSet, ToData
from commanderbot.lib.responsive_exception import ResponsiveException
from commanderbot.lib.utils import JsonPath, JsonPathOp, dict_without_ellipsis

ST = TypeVar("ST")
NT = TypeVar("NT", bound=Node)


@dataclass
class AutomodGuildData(FromData, ToData):
    """
    In-memory cache for a particular guild's automod data.

    Attributes
    ----------
    default_log_options
        Default logging configuration for this guild.
    permitted_roles
        Roles that are permitted to manage the extension within this guild.
    rules
        The guild's rules.
    buckets
        The guild's buckets.
    triggers
        The guild's triggers.
    conditions
        The guild's conditions.
    actions
        The guild's actions.
    """

    default_log_options: Optional[LogOptions] = None
    permitted_roles: Optional[RoleSet] = None

    rules: RuleCollection = field(default_factory=lambda: RuleCollection())
    buckets: BucketCollection = field(default_factory=lambda: BucketCollection())
    triggers: TriggerCollection = field(default_factory=lambda: TriggerCollection())
    conditions: ConditionCollection = field(
        default_factory=lambda: ConditionCollection()
    )
    actions: ActionCollection = field(default_factory=lambda: ActionCollection())

    # @overrides FromData
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, dict):
            default_log_options = LogOptions.from_field_optional(data, "log")
            permitted_roles = RoleSet.from_field_optional(data, "permitted_roles")
            rules = RuleCollection.from_field_default(
                data, "rules", lambda: RuleCollection()
            )
            buckets = BucketCollection.from_field_default(
                data, "buckets", lambda: BucketCollection()
            )
            triggers = TriggerCollection.from_field_default(
                data, "triggers", lambda: TriggerCollection()
            )
            conditions = ConditionCollection.from_field_default(
                data, "conditions", lambda: ConditionCollection()
            )
            actions = ActionCollection.from_field_default(
                data, "actions", lambda: ActionCollection()
            )
            return cls(
                default_log_options=default_log_options,
                permitted_roles=permitted_roles,
                rules=rules,
                buckets=buckets,
                triggers=triggers,
                conditions=conditions,
                actions=actions,
            )

    def get_collection(self, node_type: Type[NT]) -> NodeCollection[NT]:
        if node_type is Rule:
            return cast(Any, self.rules)
        if node_type is Bucket:
            return cast(Any, self.buckets)
        if node_type is Trigger:
            return cast(Any, self.triggers)
        if node_type is Condition:
            return cast(Any, self.conditions)
        if node_type is Action:
            return cast(Any, self.actions)
        raise ResponsiveException(f"Invalid node type: {node_type}")

    def set_default_log_options(
        self, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        old_value = self.default_log_options
        self.default_log_options = log_options
        return old_value

    def set_permitted_roles(
        self, permitted_roles: Optional[RoleSet]
    ) -> Optional[RoleSet]:
        old_value = self.permitted_roles
        self.permitted_roles = permitted_roles
        return old_value


def _guilds_defaultdict_factory() -> DefaultDict[GuildID, AutomodGuildData]:
    return defaultdict(lambda: AutomodGuildData())


# @implements AutomodStore
@dataclass
class AutomodData(FromData, ToData):
    """
    Implementation of `AutomodStore` using an in-memory object hierarchy.

    Attributes
    ----------
    guilds
        The guilds recorded.
    """

    guilds: DefaultDict[GuildID, AutomodGuildData] = field(
        default_factory=_guilds_defaultdict_factory
    )

    # @overrides FromData
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        guilds = _guilds_defaultdict_factory()
        guilds.update(
            {
                int(guild_id): AutomodGuildData.from_data(raw_guild_data)
                for guild_id, raw_guild_data in data.get("guilds", {}).items()
            }
        )
        return cls(guilds=guilds)

    # @overrides ToData
    def complex_fields_to_data(self) -> Optional[Dict[str, Any]]:
        # Map guild IDs to guild data, and omit empty guilds.
        return dict(
            guilds=dict_without_ellipsis(
                {
                    str(guild_id): (guild_data.to_data() or ...)
                    for guild_id, guild_data in self.guilds.items()
                }
            )
        )

    # @@ OPTIONS

    # @implements AutomodStore
    async def get_default_log_options(self, guild: Guild) -> Optional[LogOptions]:
        return self.guilds[guild.id].default_log_options

    # @implements AutomodStore
    async def set_default_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        return self.guilds[guild.id].set_default_log_options(log_options)

    # @implements AutomodStore
    async def get_permitted_roles(self, guild: Guild) -> Optional[RoleSet]:
        return self.guilds[guild.id].permitted_roles

    # @implements AutomodStore
    async def set_permitted_roles(
        self, guild: Guild, permitted_roles: Optional[RoleSet]
    ) -> Optional[RoleSet]:
        return self.guilds[guild.id].set_permitted_roles(permitted_roles)

    # @@ NODES

    # @implements AutomodStore
    async def all_nodes(self, guild: Guild, node_type: Type[NT]) -> AsyncIterable[NT]:
        collection = self.guilds[guild.id].get_collection(node_type)
        for node in collection:
            yield node

    # @implements AutomodStore
    async def query_nodes(
        self, guild: Guild, node_type: Type[NT], query: str
    ) -> AsyncIterable[NT]:
        collection = self.guilds[guild.id].get_collection(node_type)
        for node in collection.query(query):
            yield node

    # @implements AutomodStore
    async def get_node(
        self, guild: Guild, node_type: Type[NT], name: str
    ) -> Optional[NT]:
        collection = self.guilds[guild.id].get_collection(node_type)
        return collection.get(name)

    # @implements AutomodStore
    async def require_node(self, guild: Guild, node_type: Type[NT], name: str) -> NT:
        collection = self.guilds[guild.id].get_collection(node_type)
        return collection.require(name)

    # @implements AutomodStore
    async def require_node_with_type(
        self, guild: Guild, node_type: Type[NT], name: str
    ) -> NT:
        collection = self.guilds[guild.id].get_collection(node_type)
        return collection.require_with_type(name, node_type)

    # @implements AutomodStore
    async def add_node(self, guild: Guild, node_type: Type[NT], data: Any) -> NT:
        collection = self.guilds[guild.id].get_collection(node_type)
        return collection.add_from_data(data)

    # @implements AutomodStore
    async def remove_node(self, guild: Guild, node_type: Type[NT], name: str) -> NT:
        collection = self.guilds[guild.id].get_collection(node_type)
        return collection.remove_by_name(name)

    # @implements AutomodStore
    async def modify_node(
        self,
        guild: Guild,
        node_type: Type[NT],
        name: str,
        path: JsonPath,
        op: JsonPathOp,
        data: Any,
    ) -> NT:
        collection = self.guilds[guild.id].get_collection(node_type)
        return collection.modify(name, path, op, data)

    # @@ RULES

    # @implements AutomodStore
    async def rules_for_event(
        self, guild: Guild, event: AutomodEvent
    ) -> AsyncIterable[Rule]:
        async for rule in self.guilds[guild.id].rules.for_event(event):
            yield rule

    # @implements AutomodStore
    async def enable_rule(self, guild: Guild, name: str) -> Rule:
        return self.guilds[guild.id].rules.enable_by_name(name)

    # @implements AutomodStore
    async def disable_rule(self, guild: Guild, name: str) -> Rule:
        return self.guilds[guild.id].rules.disable_by_name(name)

    # @implements AutomodStore
    async def increment_rule_hits(self, guild: Guild, name: str) -> Rule:
        return self.guilds[guild.id].rules.increment_hits_by_name(name)
