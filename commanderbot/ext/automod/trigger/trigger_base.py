from dataclasses import dataclass
from typing import ClassVar, Tuple, Type

from commanderbot.ext.automod import triggers
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.component import ComponentBase

__all__ = ("TriggerBase",)


# @implements Trigger
@dataclass
class TriggerBase(ComponentBase):
    # @implements ComponentBase
    default_module_prefix: ClassVar[str] = triggers.__name__

    # @implements ComponentBase
    module_function_name: ClassVar[str] = "create_trigger"

    event_types: ClassVar[Tuple[Type[AutomodEvent], ...]] = tuple()

    async def poll(self, event: AutomodEvent) -> bool:
        # Verify that we care about this event type.
        event_type = type(event)
        if event_type not in self.event_types:
            return False

        # Check whether the event should be ignored.
        if await self.ignore(event):
            return False

        # If we get here, we probably care about the event.
        return True

    async def ignore(self, event: AutomodEvent) -> bool:
        """Override this if more than just the event type needs to be checked."""
        return False
