from dataclasses import dataclass
from typing import ClassVar, Tuple, Type

from commanderbot.ext.automod import triggers
from commanderbot.ext.automod.component import ComponentBase
from commanderbot.ext.automod.event import Event

__all__ = ("TriggerBase",)


# @implements ComponentBase
# @implements Trigger
@dataclass
class TriggerBase(ComponentBase):
    # @implements ComponentBase
    default_module_prefix: ClassVar[str] = triggers.__name__

    # @implements ComponentBase
    module_function_name: ClassVar[str] = "create_trigger"

    # @implements Trigger
    event_types: ClassVar[Tuple[Type[Event], ...]] = tuple()

    # @implements Trigger
    async def poll(self, event: Event) -> bool:
        # Skip if we're disabled.
        if self.disabled:
            return False

        # Skip unless we care about this event type.
        event_type = type(event)
        if event_type not in self.event_types:
            return False

        # Skip if the event should be ignored.
        if await self.ignore(event):
            return False

        # If we get here, we probably care about the event.
        return True

    async def ignore(self, event: Event) -> bool:
        """Override this if more than just the event type needs to be checked."""
        return False
