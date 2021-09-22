from dataclasses import dataclass
from typing import ClassVar, Type

from commanderbot.ext.automod.bucket.bucket import Bucket
from commanderbot.ext.automod.bucket.bucket_base import BucketBase
from commanderbot.ext.automod.component import ComponentCollection

__all__ = ("BucketCollection",)


@dataclass(init=False)
class BucketCollection(ComponentCollection[Bucket]):
    """A collection of buckets."""

    # @implements NodeCollection
    node_type: ClassVar[Type[Bucket]] = BucketBase
