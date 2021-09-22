from typing import Protocol

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.component import Component

__all__ = ("Bucket",)


class Bucket(Component, Protocol):
    """A bucket can be used to carry state through multiple events."""

    async def add(self, event: AutomodEvent):
        """Add the event to the bucket."""
