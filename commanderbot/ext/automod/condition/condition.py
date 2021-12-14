from typing import Protocol

from commanderbot.ext.automod.component import Component
from commanderbot.ext.automod.event import Event

__all__ = ("Condition",)


class Condition(Component, Protocol):
    """A condition is a predicate that must pass in order to run actions."""

    async def check(self, event: Event) -> bool:
        """Check whether the condition passes."""
