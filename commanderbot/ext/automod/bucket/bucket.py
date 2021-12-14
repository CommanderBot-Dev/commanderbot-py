from typing import Protocol

from commanderbot.ext.automod.component import Component
from commanderbot.ext.automod.event import Event

__all__ = ("Bucket",)


class Bucket(Component, Protocol):
    """A bucket can be used to carry state through multiple events."""

    async def add(self, event: Event):
        """Add the event to the bucket."""
