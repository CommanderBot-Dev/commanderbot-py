from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from commanderbot.ext.automod.action import ActionCollection
from commanderbot.ext.automod.condition import ConditionCollection
from commanderbot.ext.automod.event import Event
from commanderbot.ext.automod.node.node_base import NodeBase
from commanderbot.ext.automod.trigger import TriggerCollection
from commanderbot.lib import LogOptions
from commanderbot.lib.utils import datetime_from_field_optional


@dataclass
class Rule(NodeBase):
    """
    A piece of logic detailing how to perform an automated task.

    Attributes
    ----------
    added_on
        The datetime the rule was created.
    modified_on
        The last datetime the rule was modified.
    hits
        How many times the rule's conditions have passed and actions have run.
    log
        Override logging configuration for this rule.
    triggers
        A list of events that may trigger the rule.
    conditions
        A list of conditions that must *all* pass for the actions to run.
    actions
        A list of actions that will all run if the conditions pass.
    """

    added_on: datetime
    modified_on: datetime
    hits: int

    log: Optional[LogOptions]

    triggers: TriggerCollection
    conditions: ConditionCollection
    actions: ActionCollection

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        now = datetime.utcnow()
        added_on = datetime_from_field_optional(data, "added_on") or now
        modified_on = datetime_from_field_optional(data, "modified_on") or now
        triggers = (
            TriggerCollection.from_field_optional(data, "triggers")
            or TriggerCollection()
        )
        conditions = (
            ConditionCollection.from_field_optional(data, "conditions")
            or ConditionCollection()
        )
        actions = (
            ActionCollection.from_field_optional(data, "actions") or ActionCollection()
        )
        return dict(
            added_on=added_on,
            modified_on=modified_on,
            hits=data.get("hits", 0),
            log=LogOptions.from_field_optional(data, "log"),
            triggers=triggers,
            conditions=conditions,
            actions=actions,
        )

    def __hash__(self) -> int:
        return hash(self.name)

    # @overrides NodeBase
    def build_title(self) -> str:
        parts = []
        if self.disabled:
            parts.append("(Disabled)")
        parts.append(super().build_title())
        return " ".join(parts)

    async def poll_triggers(self, event: Event) -> bool:
        """Check whether the event activates any triggers."""
        for trigger in self.triggers:
            if await trigger.poll(event):
                return True
        return False

    async def check_conditions(self, event: Event) -> bool:
        """Check whether all conditions pass."""
        for condition in self.conditions:
            if not await condition.check(event):
                return False
        return True

    async def apply_actions(self, event: Event):
        """Apply all actions."""
        for action in self.actions:
            await action.apply(event)

    async def run(self, event: Event) -> bool:
        """Apply actions if conditions pass."""
        if (not self.disabled) and await self.check_conditions(event):
            await self.apply_actions(event)
            return True
        return False
