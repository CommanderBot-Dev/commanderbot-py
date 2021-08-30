from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Protocol

from commanderbot_ext.ext.automod import actions
from commanderbot_ext.ext.automod.automod_entity import (
    AutomodEntity,
    AutomodEntityBase,
    deserialize_entities,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent


class AutomodAction(AutomodEntity, Protocol):
    description: Optional[str]

    async def apply(self, event: AutomodEvent):
        """Apply the action."""


# @implements AutomodAction
@dataclass
class AutomodActionBase(AutomodEntityBase):
    """
    Base action for inheriting base fields and functionality.

    Attributes
    ----------
    description
        A human-readable description of the action.
    """

    default_module_prefix = actions.__name__
    module_function_name = "create_action"

    description: Optional[str]

    async def apply(self, event: AutomodEvent):
        """Override this to apply the action."""


def deserialize_actions(data: Iterable[Any]) -> List[AutomodAction]:
    return deserialize_entities(
        entity_type=AutomodActionBase,
        data=data,
        defaults={
            "description": None,
        },
    )
