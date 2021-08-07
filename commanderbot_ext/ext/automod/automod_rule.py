from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from commanderbot_ext.ext.automod.automod_action import (
    AutomodAction,
    deserialize_actions,
)
from commanderbot_ext.ext.automod.automod_condition import (
    AutomodCondition,
    deserialize_conditions,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.ext.automod.automod_trigger import (
    AutomodTrigger,
    deserialize_triggers,
)
from commanderbot_ext.lib import JsonObject
from commanderbot_ext.lib.utils import datetime_from_data


@dataclass
class AutomodRule:
    """
    A piece of logic detailing how to perform an automated task.

    Attributes
    ----------
    name
        The name of the rule. Can be any arbitrary string, but snake_case tends to be
        easier to type into Discord chat.
    added_on
        The datetime the rule was created.
    modified_on
        The last datetime the rule was modified.
    disabled
        Whether the rule is currently disabled.
    hits
        How many times the rule's conditions have passed and actions have run.
    description
        A human-readable description of the rule.
    triggers
        A list of events that may trigger the rule.
    conditions
        A list of conditions that must *all* pass for the actions to run.
    actions
        A list of actions that will all run if the conditions pass.
    """

    name: str
    added_on: datetime
    modified_on: datetime
    disabled: bool
    hits: int

    description: Optional[str]

    triggers: List[AutomodTrigger]
    conditions: List[AutomodCondition]
    actions: List[AutomodAction]

    @staticmethod
    def from_data(data: JsonObject) -> AutomodRule:
        now = datetime.utcnow()
        return AutomodRule(
            name=data["name"],
            added_on=datetime_from_data(data, "added_on", now),
            modified_on=datetime_from_data(data, "modified_on", now),
            disabled=data.get("disabled", False),
            hits=data.get("hits", 0),
            description=data.get("description"),
            triggers=deserialize_triggers(data.get("triggers", [])),
            conditions=deserialize_conditions(data.get("conditions", [])),
            actions=deserialize_actions(data.get("actions", [])),
        )

    def __hash__(self) -> int:
        return hash(self.name)

    def poll_triggers(self, event: AutomodEvent) -> bool:
        """Check whether the event activates any triggers."""
        for trigger in self.triggers:
            if trigger.poll(event):
                return True
        return False

    async def check_conditions(self, event: AutomodEvent) -> bool:
        """Check whether all conditions pass."""
        for condition in self.conditions:
            if not await condition.check(event):
                return False
        return True

    async def apply_actions(self, event: AutomodEvent):
        """Apply all actions."""
        for action in self.actions:
            await action.apply(event)

    async def run(self, event: AutomodEvent) -> bool:
        """Apply actions if conditions pass."""
        if await self.check_conditions(event):
            await self.apply_actions(event)
            return True
        return False
