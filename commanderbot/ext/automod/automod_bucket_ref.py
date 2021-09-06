import typing
from dataclasses import dataclass
from typing import Any, Generic, Optional, Type, TypeVar

from commanderbot.ext.automod.automod_bucket import AutomodBucket
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import FromDataMixin, JsonSerializable

ST = TypeVar("ST")
BT = TypeVar("BT", bound=AutomodBucket)


@dataclass
class BucketRef(JsonSerializable, FromDataMixin, Generic[BT]):
    name: str

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, str):
            return cls(name=data)

    # @implements JsonSerializable
    def to_json(self) -> Any:
        return self.name

    async def resolve(self, event: AutomodEvent) -> BT:
        bucket_generics = typing.get_args(self)
        bucket_type = bucket_generics[0]
        bucket = await event.state.store.require_bucket(
            event.state.guild, self.name, bucket_type
        )
        return bucket
