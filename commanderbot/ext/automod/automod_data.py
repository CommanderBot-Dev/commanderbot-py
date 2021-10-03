from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterable, DefaultDict, Dict, Iterable, Optional, Set, Type

from discord import Guild

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.automod_rule import AutomodRule
from commanderbot.lib import (
    GuildID,
    JsonObject,
    LogOptions,
    ResponsiveException,
    RoleSet,
)
from commanderbot.lib.json import to_data
from commanderbot.lib.utils import (
    JsonPath,
    JsonPathOp,
    dict_without_ellipsis,
    update_json_with_path,
)

RulesByEventType = DefaultDict[Type[AutomodEvent], Set[AutomodRule]]


class AutomodRuleWithNameAlreadyExists(ResponsiveException):
    def __init__(self, name: str):
        self.name: str = name
        super().__init__(f"A rule with the name `{name}` already exists")


class AutomodNoRuleWithName(ResponsiveException):
    def __init__(self, name: str):
        self.name: str = name
        super().__init__(f"There is no rule with the name `{name}`")


class AutomodRuleNotRegistered(ResponsiveException):
    def __init__(self, rule: AutomodRule):
        self.rule: AutomodRule = rule
        super().__init__(f"Rule `{rule.name}` is not registered")


class AutomodInvalidFields(ResponsiveException):
    def __init__(self, names: Set[str]):
        self.names: Set[str] = names
        super().__init__("These fields are invalid: " + "`" + "` `".join(names) + "`")


class AutomodUnmodifiableFields(ResponsiveException):
    def __init__(self, names: Set[str]):
        self.names: Set[str] = names
        super().__init__(
            "These fields cannot be modified: " + "`" + "` `".join(names) + "`"
        )


@dataclass
class AutomodGuildData:
    # Default logging configuration for this guild.
    default_log_options: Optional[LogOptions] = None

    # Roles that are permitted to manage the extension within this guild.
    permitted_roles: Optional[RoleSet] = None

    # Index rules by name for faster look-up in commands.
    rules: Dict[str, AutomodRule] = field(init=False, default_factory=dict)

    # Group rules by event type for faster look-up during event dispatch.
    rules_by_event_type: RulesByEventType = field(
        init=False, default_factory=lambda: defaultdict(lambda: set())
    )

    @staticmethod
    def from_data(data: JsonObject) -> AutomodGuildData:
        default_log_options = LogOptions.from_field_optional(data, "log")
        permitted_roles = RoleSet.from_field_optional(data, "permitted_roles")
        guild_data = AutomodGuildData(
            default_log_options=default_log_options,
            permitted_roles=permitted_roles,
        )
        for rule_data in data.get("rules", []):
            rule = AutomodRule.from_data(rule_data)
            guild_data.add_rule(rule)
        return guild_data

    def to_data(self) -> JsonObject:
        return dict_without_ellipsis(
            log=self.default_log_options or ...,
            permitted_roles=self.permitted_roles or ...,
            rules=list(self.rules.values()) or ...,
        )

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

    def all_rules(self) -> Iterable[AutomodRule]:
        yield from self.rules.values()

    def rules_for_event(self, event: AutomodEvent) -> Iterable[AutomodRule]:
        event_type = type(event)
        # Start with the initial set of possible rules, based on the event type.
        for rule in self.rules_by_event_type[event_type]:
            # Yield the rule if the event activates any of its triggers.
            if rule.poll_triggers(event):
                yield rule

    def query_rules(self, query: str) -> Iterable[AutomodRule]:
        # If there's an exact match, yield just that.
        if rule := self.rules.get(query):
            yield rule
        else:
            # Otherwise, yield any rules that match the query.
            query_lower = query.lower()
            for rule_name, rule in self.rules.items():
                if query_lower in rule_name.lower():
                    yield rule

    def get_rule(self, name: str) -> Optional[AutomodRule]:
        return self.rules.get(name)

    def require_rule(self, name: str) -> AutomodRule:
        if rule := self.get_rule(name):
            return rule
        raise AutomodNoRuleWithName(name)

    def _add_rule_to_cache(self, rule: AutomodRule):
        for trigger in rule.triggers:
            for event_type in trigger.event_types:
                self.rules_by_event_type[event_type].add(rule)

    def add_rule(self, rule: AutomodRule):
        if rule.name in self.rules:
            raise AutomodRuleWithNameAlreadyExists(rule.name)
        self.rules[rule.name] = rule
        self._add_rule_to_cache(rule)

    def add_rule_from_data(self, data: JsonObject) -> AutomodRule:
        rule = AutomodRule.from_data(data)
        self.add_rule(rule)
        return rule

    def _remove_rule_from_cache(self, rule: AutomodRule):
        for rules in self.rules_by_event_type.values():
            if rule in rules:
                rules.remove(rule)

    def remove_rule(self, rule: AutomodRule):
        existing_rule = self.rules.get(rule.name)
        if not (existing_rule and (existing_rule is rule)):
            raise AutomodRuleNotRegistered(rule)
        self._remove_rule_from_cache(rule)
        del self.rules[rule.name]

    def remove_rule_by_name(self, name: str) -> AutomodRule:
        rule = self.require_rule(name)
        self.remove_rule(rule)
        return rule

    def modify_rule_raw(
        self,
        name: str,
        path: JsonPath,
        op: JsonPathOp,
        data: Any,
    ) -> AutomodRule:
        # Start with the serialized form of the original rule.
        old_rule = self.require_rule(name)
        new_data = to_data(old_rule)

        # Update the modification timestamp. Note that it may still be overidden.
        new_data["modified_on"] = datetime.utcnow().isoformat()

        # Update the new rule data using the given changes.
        update_json_with_path(new_data, path, op, data)

        # Create a new rule out of the modified data.
        new_rule = AutomodRule.from_data(new_data)

        # Remove the old rule, and then add the new one.
        self.remove_rule(old_rule)
        self.add_rule(new_rule)

        # Return the new rule.
        return new_rule

    def enable_rule_by_name(self, name: str) -> AutomodRule:
        rule = self.require_rule(name)
        rule.disabled = False
        return rule

    def disable_rule_by_name(self, name: str) -> AutomodRule:
        rule = self.require_rule(name)
        rule.disabled = True
        return rule

    def increment_rule_hits_by_name(self, name: str) -> AutomodRule:
        rule = self.require_rule(name)
        rule.hits += 1
        return rule


def _guilds_defaultdict_factory() -> DefaultDict[GuildID, AutomodGuildData]:
    return defaultdict(lambda: AutomodGuildData())


# @implements AutomodStore
@dataclass
class AutomodData:
    """
    Implementation of `AutomodStore` using an in-memory object hierarchy.
    """

    guilds: DefaultDict[GuildID, AutomodGuildData] = field(
        default_factory=_guilds_defaultdict_factory
    )

    @staticmethod
    def from_data(data: JsonObject) -> AutomodData:
        guilds = _guilds_defaultdict_factory()
        guilds.update(
            {
                int(guild_id): AutomodGuildData.from_data(raw_guild_data)
                for guild_id, raw_guild_data in data.get("guilds", {}).items()
            }
        )
        return AutomodData(guilds=guilds)

    def to_data(self) -> JsonObject:
        # Omit empty guilds, as well as an empty list of guilds.
        return dict_without_ellipsis(
            guilds=dict_without_ellipsis(
                {
                    str(guild_id): (guild_data.to_data() or ...)
                    for guild_id, guild_data in self.guilds.items()
                }
            )
            or ...
        )

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

    # @implements AutomodStore
    async def all_rules(self, guild: Guild) -> AsyncIterable[AutomodRule]:
        for rule in self.guilds[guild.id].all_rules():
            yield rule

    # @implements AutomodStore
    async def rules_for_event(
        self, guild: Guild, event: AutomodEvent
    ) -> AsyncIterable[AutomodRule]:
        for rule in self.guilds[guild.id].rules_for_event(event):
            yield rule

    # @implements AutomodStore
    async def query_rules(self, guild: Guild, query: str) -> AsyncIterable[AutomodRule]:
        for rule in self.guilds[guild.id].query_rules(query):
            yield rule

    # @implements AutomodStore
    async def get_rule(self, guild: Guild, name: str) -> Optional[AutomodRule]:
        return self.guilds[guild.id].get_rule(name)

    # @implements AutomodStore
    async def require_rule(self, guild: Guild, name: str) -> AutomodRule:
        return self.guilds[guild.id].require_rule(name)

    # @implements AutomodStore
    async def add_rule(self, guild: Guild, data: JsonObject) -> AutomodRule:
        return self.guilds[guild.id].add_rule_from_data(data)

    # @implements AutomodStore
    async def remove_rule(self, guild: Guild, name: str) -> AutomodRule:
        return self.guilds[guild.id].remove_rule_by_name(name)

    # @implements AutomodStore
    async def modify_rule(
        self,
        guild: Guild,
        name: str,
        path: JsonPath,
        op: JsonPathOp,
        data: Any,
    ) -> AutomodRule:
        return self.guilds[guild.id].modify_rule_raw(name, path, op, data)

    # @implements AutomodStore
    async def enable_rule(self, guild: Guild, name: str) -> AutomodRule:
        return self.guilds[guild.id].enable_rule_by_name(name)

    # @implements AutomodStore
    async def disable_rule(self, guild: Guild, name: str) -> AutomodRule:
        return self.guilds[guild.id].disable_rule_by_name(name)

    # @implements AutomodStore
    async def increment_rule_hits(self, guild: Guild, name: str) -> AutomodRule:
        return self.guilds[guild.id].increment_rule_hits_by_name(name)
