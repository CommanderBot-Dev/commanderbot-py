from typing import ClassVar, Generic, Type, TypeVar

from commanderbot.ext.automod.action.action import Action
from commanderbot.ext.automod.action.action_base import ActionBase
from commanderbot.ext.automod.node import NodeRef

__all__ = ("ActionRef",)


NT = TypeVar("NT", bound=Action)


# @implements NodeRef
class ActionRef(NodeRef[Action], Generic[NT]):
    """A reference to an action, by name."""

    # @implements NodeRef
    node_type: ClassVar[Type[Action]] = ActionBase
