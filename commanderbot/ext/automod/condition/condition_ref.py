from typing import ClassVar, Generic, Type, TypeVar

from commanderbot.ext.automod.condition.condition import Condition
from commanderbot.ext.automod.node import NodeRef

__all__ = ("ConditionRef",)


NT = TypeVar("NT", bound=Condition)


# @implements NodeRef
class ConditionRef(NodeRef[Condition], Generic[NT]):
    """A reference to a condition, by name."""

    # @implements NodeRef
    node_type: ClassVar[Type[Condition]] = Condition
