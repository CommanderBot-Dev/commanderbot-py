from dataclasses import dataclass
from typing import (
    Any,
    ClassVar,
    Iterable,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
)

from commanderbot_ext.ext.automod import triggers
from commanderbot_ext.ext.automod.automod_entity import (
    AutomodEntity,
    AutomodEntityBase,
    deserialize_entities,
)
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib.types import JsonObject

ST = TypeVar("ST")


class AutomodTrigger(AutomodEntity, Protocol):
    event_types: ClassVar[Tuple[Type[AutomodEvent], ...]]

    description: Optional[str]

    def poll(self, event: AutomodEvent) -> Optional[bool]:
        """Check whether an event activates the trigger."""


# @implements AutomodTrigger
@dataclass
class AutomodTriggerBase(AutomodEntityBase):
    """
    Base trigger for inheriting base fields and functionality.

    Attributes
    ----------
    description
        A human-readable description of the trigger.
    """

    default_module_prefix = triggers.__name__
    module_function_name = "create_trigger"

    event_types: ClassVar[Tuple[Type[AutomodEvent], ...]] = tuple()

    description: Optional[str]

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        """Override this if the subclass defines additional fields."""
        return cls(
            description=data.get("description"),
        )

    def poll(self, event: AutomodEvent) -> bool:
        # Verify that we care about this event type.
        event_type = type(event)
        if event_type not in self.event_types:
            return False
        # Check whether the event should be ignored.
        if self.ignore(event):
            return False
        return True

    def ignore(self, event: AutomodEvent) -> bool:
        """Override this if more than just the event type needs to be checked."""
        return False


def deserialize_triggers(data: Iterable[Any]) -> List[AutomodTrigger]:
    return deserialize_entities(
        entity_type=AutomodTriggerBase,
        data=data,
        defaults={
            "description": None,
        },
    )
