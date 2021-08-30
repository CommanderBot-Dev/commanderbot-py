from typing import Any, Optional, Type, TypeVar

from commanderbot_ext.lib.data import MalformedData
from commanderbot_ext.lib.json import JsonObject

__all__ = ("FromDataMixin",)


ST = TypeVar("ST", bound="FromDataMixin")


class FromDataMixin:
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        """Override this to return an instance of the class given valid input."""
        raise NotImplementedError()

    @classmethod
    def from_data(cls: Type[ST], data: Any) -> ST:
        try:
            if (maybe_from_data := cls.try_from_data(data)) is not None:
                return maybe_from_data
        except Exception as ex:
            raise MalformedData(cls, data) from ex
        raise MalformedData(cls, data)

    @classmethod
    def from_field(cls: Type[ST], data: JsonObject, key: str) -> ST:
        return cls.from_data(data[key])

    @classmethod
    def from_field_optional(cls: Type[ST], data: JsonObject, key: str) -> Optional[ST]:
        if raw_value := data.get(key):
            return cls.from_data(raw_value)
