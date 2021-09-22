from typing import Protocol

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.component import Component

__all__ = ("Action",)


class Action(Component, Protocol):
    """An action defines a task to perform when conditions pass."""

    async def apply(self, event: AutomodEvent):
        """Apply the action."""
