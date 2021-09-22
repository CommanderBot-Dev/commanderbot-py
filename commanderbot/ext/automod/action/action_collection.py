from dataclasses import dataclass
from typing import ClassVar, Type

from commanderbot.ext.automod.action.action import Action
from commanderbot.ext.automod.action.action_base import ActionBase
from commanderbot.ext.automod.component import ComponentCollection

__all__ = ("ActionCollection",)


@dataclass(init=False)
class ActionCollection(ComponentCollection[Action]):
    """A collection of actions."""

    # @implements NodeCollection
    node_type: ClassVar[Type[Action]] = ActionBase
