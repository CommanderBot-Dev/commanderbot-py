from dataclasses import dataclass
from typing import Type, TypeVar

from commanderbot.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot.ext.automod.automod_bucket import AutomodBucket
from commanderbot.ext.automod.automod_bucket_ref import BucketRef
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject

ST = TypeVar("ST")


@dataclass
class AddToBucket(AutomodActionBase):
    """
    Add the event to a bucket.

    Attributes
    ----------
    bucket
        The bucket to add to.
    """

    bucket: BucketRef[AutomodBucket]

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        bucket = BucketRef.from_field(data, "bucket")
        return cls(
            description=data.get("description"),
            bucket=bucket,
        )

    async def apply(self, event: AutomodEvent):
        # Resolve the bucket and add the event to it.
        bucket = await self.bucket.resolve(event)
        await bucket.add(event)


def create_action(data: JsonObject) -> AutomodAction:
    return AddToBucket.from_data(data)
