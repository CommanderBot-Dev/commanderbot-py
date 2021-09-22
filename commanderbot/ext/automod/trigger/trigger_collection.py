from dataclasses import dataclass
from typing import ClassVar, Type

from commanderbot.ext.automod.component import ComponentCollection
from commanderbot.ext.automod.trigger.trigger import Trigger
from commanderbot.ext.automod.trigger.trigger_base import TriggerBase

__all__ = ("TriggerCollection",)


@dataclass(init=False)
class TriggerCollection(ComponentCollection[Trigger]):
    """A collection of triggers."""

    # @implements NodeCollection
    node_type: ClassVar[Type[Trigger]] = TriggerBase
