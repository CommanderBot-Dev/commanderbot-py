from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from discord import Colour

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
from commanderbot_ext.lib import ChannelID, JsonObject
from commanderbot_ext.lib.utils import (
    color_from_hex,
    color_to_hex,
    dict_without_ellipsis,
)


@dataclass
class AutomodRule:
    name: str
    added_on: datetime
    modified_on: datetime

    # How many times the rule has been activated. (triggers -> conditions -> actions)
    hits: int

    description: Optional[str]

    log_channel: Optional[ChannelID]
    log_emoji: Optional[str]
    log_icon: Optional[str]
    log_color: Optional[Colour]

    triggers: List[AutomodTrigger]
    conditions: List[AutomodCondition]
    actions: List[AutomodAction]

    @staticmethod
    def from_data(data: JsonObject) -> AutomodRule:
        now = datetime.utcnow()
        added_on: datetime = now
        if raw_added_on := data.get("added_on"):
            added_on = datetime.fromisoformat(raw_added_on)
        modified_on: datetime = now
        if raw_modified_on := data.get("modified_on"):
            modified_on = datetime.fromisoformat(raw_modified_on)
        log_color: Optional[Colour] = None
        if raw_color := data.get("log_color"):
            log_color = color_from_hex(raw_color)
        triggers = deserialize_triggers(data.get("triggers", []))
        conditions = deserialize_conditions(data.get("conditions", []))
        actions = deserialize_actions(data.get("actions", []))
        return AutomodRule(
            name=data["name"],
            added_on=added_on,
            modified_on=modified_on,
            hits=data.get("hits", 0),
            description=data.get("description"),
            log_channel=data.get("log_channel"),
            log_emoji=data.get("log_emoji"),
            log_icon=data.get("log_icon"),
            log_color=log_color,
            triggers=triggers,
            conditions=conditions,
            actions=actions,
        )

    def __hash__(self) -> int:
        return hash(self.name)

    def to_data(self) -> JsonObject:
        return dict_without_ellipsis(
            name=self.name,
            added_on=self.added_on.isoformat(),
            modified_on=self.modified_on.isoformat(),
            hits=self.hits,
            description=self.description or ...,
            log_channel=self.log_channel or ...,
            log_emoji=self.log_emoji or ...,
            log_icon=self.log_icon or ...,
            log_color=color_to_hex(self.log_color) if self.log_color else ...,
            triggers=[trigger.to_data() for trigger in self.triggers] or ...,
            conditions=[condition.to_data() for condition in self.conditions] or ...,
            actions=[action.to_data() for action in self.actions] or ...,
        )

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
