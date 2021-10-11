from typing import ClassVar, Generic, Type, TypeVar

from commanderbot.ext.automod.bucket.bucket import Bucket
from commanderbot.ext.automod.bucket.bucket_base import BucketBase
from commanderbot.ext.automod.node import NodeRef

__all__ = ("BucketRef",)


NT = TypeVar("NT", bound=Bucket)


class BucketRef(NodeRef[NT], Generic[NT]):
    """A reference to a bucket, by name."""

    # @implements NodeRef
    node_type: ClassVar[Type[Bucket]] = BucketBase
