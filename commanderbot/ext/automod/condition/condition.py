from typing import Protocol

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.component import Component

__all__ = ("Condition",)


class Condition(Component, Protocol):
    """A condition is a predicate that must pass in order to run actions."""

    async def check(self, event: AutomodEvent) -> bool:
        """Check whether the condition passes."""
