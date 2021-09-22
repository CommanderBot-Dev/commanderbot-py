from dataclasses import dataclass
from typing import ClassVar, Type

from commanderbot.ext.automod.component import ComponentCollection
from commanderbot.ext.automod.condition.condition import Condition
from commanderbot.ext.automod.condition.condition_base import ConditionBase

__all__ = ("ConditionCollection",)


@dataclass(init=False)
class ConditionCollection(ComponentCollection[Condition]):
    """A collection of conditions."""

    # @implements NodeCollection
    node_type: ClassVar[Type[Condition]] = ConditionBase
