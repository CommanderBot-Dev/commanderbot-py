from typing import TypeVar

from commanderbot.ext.automod.action.action import Action
from commanderbot.ext.automod.node import NodeRef

__all__ = ("ActionRef",)


NT = TypeVar("NT", bound=Action)


class ActionRef(NodeRef[NT]):
    """A reference to an action, by name."""
