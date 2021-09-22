import dataclasses
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, cast

from discord import Color

__all__ = (
    "MalformedData",
    "FromData",
    "ToData",
)


MISSING = object()


class MalformedData(Exception):
    def __init__(self, cls: Type, data: Any):
        super().__init__(f"Cannot create {cls.__name__} from {type(data).__name__}")


ST = TypeVar("ST", bound="FromData")


class FromData:
    """Something that can be deserialized from raw data into an object."""

    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        """
        Attempt to construct an instance of `cls` from raw `data`.

        An implementation of this method only needs to account for valid cases.

        It is recommended to use `from_data` as a wrapper around this method. In this
        case if `None` (or nothing at all) is returned, or an error is thrown, a new
        error will be thrown that wraps the original with additional context.
        """
        if isinstance(data, dict):
            # We're only doing this to satisfy type-checking. It may or may not work
            # during runtime, but it should be wrapped in an error handler regardless.
            maybe_constructor = cast(Callable[[Any], ST], cls)
            return maybe_constructor(**data)

    @classmethod
    def from_data(cls: Type[ST], data: Any) -> ST:
        """Construct an instance of `cls` from raw `data`."""
        try:
            if (maybe_from_data := cls.try_from_data(data)) is not None:
                return maybe_from_data
        except Exception as ex:
            raise MalformedData(cls, data) from ex
        raise MalformedData(cls, data)

    @classmethod
    def from_field(cls: Type[ST], data: Dict[str, Any], key: str) -> ST:
        """Construct an instance of `cls` from a field of `data`."""
        return cls.from_data(data[key])

    @classmethod
    def from_field_optional(
        cls: Type[ST], data: Dict[str, Any], key: str
    ) -> Optional[ST]:
        """Optionally construct an instance of `cls` from a field of `data`."""
        if raw_value := data.get(key):
            return cls.from_data(raw_value)

    @classmethod
    def from_field_default(
        cls: Type[ST],
        data: Dict[str, Any],
        key: str,
        default_factory: Callable[[], ST],
    ) -> ST:
        """Construct an instance of `cls` from a field of `data` or return a default."""
        if raw_value := data.get(key):
            return cls.from_data(raw_value)
        return default_factory()


class ToData:
    """An object that can be serialized into raw data."""

    @classmethod
    def attributes_to_data(cls, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Convert object attributes to data."""
        return {k: cls.attribute_to_data(v) for k, v in attrs.items()}

    @classmethod
    def set_to_data(cls, value: set) -> List[Any]:
        return list(value)

    @classmethod
    def datetime_to_data(cls, value: datetime) -> str:
        return value.isoformat()

    @classmethod
    def timedelta_to_data(cls, value: timedelta) -> Dict[str, int]:
        return dict(
            days=value.days,
            seconds=value.seconds,
            microseconds=value.microseconds,
        )

    @classmethod
    def color_to_data(cls, value: Color) -> str:
        return str(value)

    @classmethod
    def attribute_to_data(cls, value: Any) -> Any:
        """Convert an attribute to data, if possible."""
        if isinstance(value, ToData):
            return value.to_data()
        if dataclasses.is_dataclass(value):
            return cls.attributes_to_data(value.__dict__)
        if isinstance(value, set):
            return cls.set_to_data(value)
        if isinstance(value, datetime):
            return cls.datetime_to_data(value)
        if isinstance(value, timedelta):
            return cls.timedelta_to_data(value)
        if isinstance(value, Color):
            return cls.color_to_data(value)
        return value

    def to_data(self) -> Any:
        """Turn the object into raw data."""
        # Start with a new, empty copy of data.
        data: Dict[str, Any] = {}

        # Update with base fields, if any.
        if base_fields := self.base_fields_to_data():
            data.update(base_fields)

        # Update with converted fields from `__dict__`.
        converted_attributes = self.attributes_to_data(self.__dict__)
        data.update(converted_attributes)

        # Update with additional complex fields, if any.
        if complex_fields := self.complex_fields_to_data():
            data.update(complex_fields)

        # Return the final, converted data.
        return data

    def base_fields_to_data(self) -> Optional[Dict[str, Any]]:
        """
        Convert base fields into raw data, if any.

        Override this if the inheriting class has base fields that are not present on
        instances of the class, but should be included in data.
        """

    def complex_fields_to_data(self) -> Optional[Dict[str, Any]]:
        """
        Convert complex fields into raw data, if any.

        Override this if the inheriting class has additional attributes that require
        special handling to be converted into data.
        """
