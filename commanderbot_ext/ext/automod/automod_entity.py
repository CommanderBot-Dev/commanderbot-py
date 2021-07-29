from typing import (
    Any,
    ClassVar,
    Dict,
    Iterable,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
)

from commanderbot_ext.ext.automod.utils import deserialize_module_object
from commanderbot_ext.lib import JsonObject
from commanderbot_ext.lib.utils import dict_without_ellipsis

SelfType = TypeVar("SelfType")


class AutomodEntity(Protocol):
    """Base interface for automod triggers, conditions, and actions."""

    @classmethod
    def from_data(cls: Type[SelfType], data: JsonObject) -> SelfType:
        """Create an entity from data."""

    def to_data(self) -> JsonObject:
        """Turn the entity into data."""


# @implements AutomodEntity
class AutomodEntityBase:
    """
    Contains common base logic for automod triggers, conditions, and actions.

    This includes logic for using the `type` field to load a python module and call one
    of its functions to deserialize the given data and create a new object.
    """

    default_module_prefix: ClassVar[str] = ""
    module_function_name: ClassVar[str] = ""

    ST = TypeVar("ST", bound="AutomodEntityBase")

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        """Override this if any fields require special handling."""
        return cls(**data)

    def __init__(self, *args, **kwargs):
        pass

    def to_data(self) -> JsonObject:
        data = {}
        data["type"] = self.serialize_type()
        fields = self.serialize_fields()
        data.update(fields)
        return data

    def serialize_type(self) -> str:
        """Override this if the external type field requires special handling."""
        if not self.default_module_prefix:
            raise ValueError(
                f"Subclass of {AutomodEntityBase.__name__} lacks a"
                + " `default_module_prefix`"
            )
        default_check = f"{self.default_module_prefix}."
        long_type = self.__class__.__module__
        if long_type.startswith(default_check):
            short_type = long_type[len(default_check) :]
            return short_type
        return long_type

    def serialize_fields(self) -> JsonObject:
        data = self.__dict__.copy()
        if (special_fields := self.serialize_special_fields()) is not None:
            data.update(special_fields)
        data = dict_without_ellipsis(data)
        return data

    def serialize_special_fields(self) -> Optional[JsonObject]:
        """Override this if any fields require special handling."""


ET = TypeVar("ET", bound="AutomodEntityBase")


def deserialize_entity(
    entity_type: Type[ET],
    data: Any,
    defaults: Optional[Dict[str, Any]] = None,
) -> ET:
    """
    Create an entity from raw data.

    Note that the raw data should usually be an object with key-value pairs, but in the
    case that a string is provided it will be used to populate the `type` field along
    with any `defaults` given.
    """
    # prepare the processed data
    processed_data: Dict[str, Any] = defaults.copy() if defaults else {}
    if isinstance(data, dict):
        processed_data.update(data)
    elif isinstance(data, str):
        processed_data["type"] = data
    else:
        raise ValueError(data)
    # deserialize the action
    return deserialize_module_object(
        data=processed_data,
        default_module_prefix=entity_type.default_module_prefix,
        function_name=entity_type.module_function_name,
    )


def deserialize_entities(
    entity_type: Type[ET],
    data: Iterable[Any],
    defaults: Optional[Dict[str, Any]] = None,
) -> List[ET]:
    """
    Create a list of entities from raw data.

    Use `defaults` to provide default values for things like optional dataclass fields.
    """
    return [
        deserialize_entity(
            data=value,
            entity_type=entity_type,
            defaults=defaults,
        )
        for value in data
    ]
