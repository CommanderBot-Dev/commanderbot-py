from typing import ClassVar, Optional, Protocol, Tuple, Type

from commanderbot.ext.automod.component import Component
from commanderbot.ext.automod.event import Event

__all__ = ("Trigger",)


class Trigger(Component, Protocol):
    """A trigger details precisely which events to listen for."""

    event_types: ClassVar[Tuple[Type[Event], ...]]

    async def poll(self, event: Event) -> Optional[bool]:
        """Check whether an event activates the trigger."""
