from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import (
    Any,
    AsyncIterable,
    ClassVar,
    DefaultDict,
    Iterable,
    Optional,
    Set,
    Type,
)

from commanderbot.ext.automod.event import Event
from commanderbot.ext.automod.node import NodeCollection
from commanderbot.ext.automod.rule.rule import Rule
from commanderbot.lib.utils import JsonPath, JsonPathOp

__all__ = ("RuleCollection",)


RuleBase = Rule


@dataclass(init=False)
class RuleCollection(NodeCollection[Rule]):
    """A collection of rules."""

    # @implements NodeCollection
    node_type: ClassVar[Type[Rule]] = RuleBase

    # Index rules by event type for faster look-up during event dispatch.
    _rules_by_event_type: DefaultDict[Type[Event], Set[Rule]]

    # @overrides NodeCollection
    def __init__(self, nodes: Optional[Iterable[Rule]] = None):
        self._rules_by_event_type = defaultdict(lambda: set())
        super().__init__(nodes)

    # @overrides NodeCollection
    def _add_to_cache(self, node: Rule):
        super()._add_to_cache(node)
        rule = node
        # Add the rule to the event index.
        for trigger in rule.triggers:
            for event_type in trigger.event_types:
                self._rules_by_event_type[event_type].add(rule)

    # @overrides NodeCollection
    def _remove_from_cache(self, node: Rule):
        super()._remove_from_cache(node)
        rule = node
        # Remove the rule from the event index.
        for rules_for_event_type in self._rules_by_event_type.values():
            if rule in rules_for_event_type:
                rules_for_event_type.remove(rule)

    # @overrides NodeCollection
    def modify(self, name: str, path: JsonPath, op: JsonPathOp, data: Any) -> Rule:
        # Update the rule's "modified on" timestamp.
        rule = super().modify(name, path, op, data)
        rule.modified_on = datetime.utcnow()
        return rule

    async def for_event(self, event: Event) -> AsyncIterable[Rule]:
        event_type = type(event)
        # Start with the initial set of possible rules, based on the event type.
        for rule in self._rules_by_event_type[event_type]:
            # Yield the rule if the event activates any of its triggers.
            if await rule.poll_triggers(event):
                yield rule

    def increment_hits_by_name(self, name: str) -> Rule:
        rule = self.require(name)
        rule.hits += 1
        return rule
