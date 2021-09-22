from typing import ClassVar, Optional, Protocol, Tuple, Type

from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.component import Component

__all__ = ("Trigger",)


class Trigger(Component, Protocol):
    """A trigger details precisely which events to listen for."""

    event_types: ClassVar[Tuple[Type[AutomodEvent], ...]]

    async def poll(self, event: AutomodEvent) -> Optional[bool]:
        """Check whether an event activates the trigger."""
