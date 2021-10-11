from dataclasses import dataclass
from typing import Any, Dict, Optional

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.bucket import BucketRef
from commanderbot.ext.automod.event import Event


@dataclass
class AddToBucket(ActionBase):
    """
    Add the event to a bucket.

    Attributes
    ----------
    bucket
        The bucket to add to.
    """

    bucket: BucketRef

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        bucket = BucketRef.from_field(data, "bucket")
        return dict(
            bucket=bucket,
        )

    async def apply(self, event: Event):
        # Resolve the bucket and add the event to it.
        bucket = await self.bucket.resolve(event)
        await bucket.add(event)


def create_action(data: Any) -> Action:
    return AddToBucket.from_data(data)
