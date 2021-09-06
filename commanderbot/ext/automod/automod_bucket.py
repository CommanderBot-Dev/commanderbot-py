from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Protocol

from commanderbot.ext.automod import buckets
from commanderbot.ext.automod.automod_entity import (
    AutomodEntity,
    AutomodEntityBase,
    deserialize_entities,
)
from commanderbot.ext.automod.automod_event import AutomodEvent


class AutomodBucket(AutomodEntity, Protocol):
    description: Optional[str]

    async def add(self, event: AutomodEvent):
        """Add the event to the bucket."""


# @implements AutomodBucket
@dataclass
class AutomodBucketBase(AutomodEntityBase):
    """
    Base bucket for inheriting base fields and functionality.

    Attributes
    ----------
    description
        A human-readable description of the bucket.
    """

    default_module_prefix = buckets.__name__
    module_function_name = "create_bucket"

    description: Optional[str]

    async def add(self, event: AutomodEvent):
        """Override this to modify the bucket according to the event."""


def deserialize_buckets(data: Iterable[Any]) -> List[AutomodBucket]:
    return deserialize_entities(
        entity_type=AutomodBucketBase,
        data=data,
        defaults={
            "description": None,
        },
    )
