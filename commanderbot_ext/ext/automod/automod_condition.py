from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Protocol

from commanderbot_ext.ext.automod import conditions
from commanderbot_ext.ext.automod.automod_entity import (
    AutomodEntity,
    AutomodEntityBase,
    deserialize_entities,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent


class AutomodCondition(AutomodEntity, Protocol):
    description: Optional[str]

    async def check(self, event: AutomodEvent) -> bool:
        """Check whether the condition passes."""


# @implements AutomodCondition
@dataclass
class AutomodConditionBase(AutomodEntityBase):
    """
    Base condition for inheriting base fields and functionality.

    Attributes
    ----------
    description
        A human-readable description of the condition.
    """

    default_module_prefix = conditions.__name__
    module_function_name = "create_condition"

    description: Optional[str]

    async def check(self, event: AutomodEvent) -> bool:
        """Override this to check whether the condition passes."""
        return False


def deserialize_conditions(data: Iterable[Any]) -> List[AutomodCondition]:
    return deserialize_entities(
        entity_type=AutomodConditionBase,
        data=data,
        defaults={
            "description": None,
        },
    )
