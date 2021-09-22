from typing import TypeVar

from commanderbot.ext.automod.bucket.bucket import Bucket
from commanderbot.ext.automod.node import NodeRef

__all__ = ("BucketRef",)


NT = TypeVar("NT", bound=Bucket)


class BucketRef(NodeRef[NT]):
    """A reference to a bucket, by name."""
