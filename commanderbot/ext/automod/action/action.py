from typing import Protocol

from commanderbot.ext.automod.component import Component
from commanderbot.ext.automod.event import Event

__all__ = ("Action",)


class Action(Component, Protocol):
    """An action defines a task to perform when conditions pass."""

    async def apply(self, event: Event):
        """Apply the action."""
