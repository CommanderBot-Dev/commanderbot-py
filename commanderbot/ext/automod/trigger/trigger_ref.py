from typing import TypeVar

from commanderbot.ext.automod.node import NodeRef
from commanderbot.ext.automod.trigger.trigger import Trigger

__all__ = ("TriggerRef",)


NT = TypeVar("NT", bound=Trigger)


class TriggerRef(NodeRef[NT]):
    """A reference to a trigger, by name."""
