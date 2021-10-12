import dataclasses
from collections import defaultdict
from datetime import datetime, timedelta
from typing import (
    Any,
    Callable,
    ClassVar,
    Collection,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    cast,
)

from discord import Color

from commanderbot.lib.errors import MalformedData
from commanderbot.lib.utils.dataclasses import is_field_optional

__all__ = (
    "FromData",
    "ToData",
)


MISSING = object()


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

    class Flags:
        ExcludeFromData: ClassVar[str] = "exclude_from_data"

    @classmethod
    def attributes_to_dict(cls, value: object) -> Dict[str, Any]:
        if dataclasses.is_dataclass(value):
            return cls.dataclass_to_dict(value)
        return dict(value.__dict__)

    @classmethod
    def dataclass_to_dict(cls, value: object) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        for field in dataclasses.fields(value):
            # Check for field flags.
            flags = field.metadata.get(cls.Flags)
            if isinstance(flags, tuple | list | set):
                # Skip excluded fields.
                if cls.Flags.ExcludeFromData in flags:
                    continue

            # Get the field value.
            field_value = getattr(value, field.name)

            # Skip optional fields with a null value.
            if (field_value is None) and is_field_optional(field):
                continue

            # If we get here, include the final field value.
            d[field.name] = field_value

        return d

    @classmethod
    def value_to_data(cls, value: Any) -> Any:
        """Convert a value to data, if possible."""
        if isinstance(value, ToData):
            return value.to_data()
        if dataclasses.is_dataclass(value):
            return cls.dataclass_to_data(value)
        if isinstance(value, dict | defaultdict):
            return cls.mapping_to_data(value)
        if isinstance(value, tuple | list | set):
            return cls.collection_to_data(value)
        if isinstance(value, datetime):
            return cls.datetime_to_data(value)
        if isinstance(value, timedelta):
            return cls.timedelta_to_data(value)
        if isinstance(value, Color):
            return cls.color_to_data(value)
        return value

    @classmethod
    def dataclass_to_data(cls, value: object) -> Dict[str, Any]:
        attrs = cls.attributes_to_dict(value)
        return cls.mapping_to_data(attrs)

    @classmethod
    def mapping_to_data(cls, value: Mapping[Any, Any]) -> Dict[Any, Any]:
        return {k: cls.value_to_data(v) for k, v in value.items()}

    @classmethod
    def collection_to_data(cls, value: Collection[Any]) -> List[Any]:
        return [cls.value_to_data(v) for v in value]

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

    def to_data(self) -> Any:
        """Turn the object into raw data."""
        # Start with a new, empty copy of data.
        data: Dict[str, Any] = {}

        # Update with base fields, if any.
        if base_fields := self.base_fields_to_data():
            data.update(base_fields)

        # Get base instance attributes as a dict.
        instance_attrs = self.attributes_to_dict(self)

        # Update with converted attributes.
        converted_attrs = self.mapping_to_data(instance_attrs)
        data.update(converted_attrs)

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

    def exclude_fields_to_data(self) -> Optional[Tuple[str, ...]]:
        """
        Exclude certain fields from data, if any.

        Override this if the inheriting class has certain attributes that should not be
        included in data.
        """

    def complex_fields_to_data(self) -> Optional[Dict[str, Any]]:
        """
        Convert complex fields into raw data, if any.

        Override this if the inheriting class has additional attributes that require
        special handling to be converted into data.
        """
