from typing import ClassVar, Generic, Type, TypeVar

from commanderbot.ext.automod.node import NodeRef
from commanderbot.ext.automod.trigger.trigger import Trigger
from commanderbot.ext.automod.trigger.trigger_base import TriggerBase

__all__ = ("TriggerRef",)


NT = TypeVar("NT", bound=Trigger)


# @implements NodeRef
class TriggerRef(NodeRef[Trigger], Generic[NT]):
    """A reference to a trigger, by name."""

    # @implements NodeRef
    node_type: ClassVar[Type[Trigger]] = TriggerBase
