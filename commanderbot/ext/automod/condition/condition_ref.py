from typing import TypeVar

from commanderbot.ext.automod.condition.condition import Condition
from commanderbot.ext.automod.node import NodeRef

__all__ = ("ConditionRef",)


NT = TypeVar("NT", bound=Condition)


class ConditionRef(NodeRef[NT]):
    """A reference to a condition, by name."""
