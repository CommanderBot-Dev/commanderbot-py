from dataclasses import dataclass
from typing import ClassVar

from commanderbot.ext.automod import buckets
from commanderbot.ext.automod.component import ComponentBase
from commanderbot.ext.automod.event import Event

__all__ = ("BucketBase",)


# @implements ComponentBase
# @implements Bucket
@dataclass
class BucketBase(ComponentBase):
    # @implements ComponentBase
    default_module_prefix: ClassVar[str] = buckets.__name__

    # @implements ComponentBase
    module_function_name: ClassVar[str] = "create_bucket"

    # @implements Bucket
    async def add(self, event: Event):
        """Override this to modify the bucket according to the event."""
