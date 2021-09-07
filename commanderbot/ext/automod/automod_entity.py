from dataclasses import dataclass
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

from commanderbot.ext.automod.utils import deserialize_module_object
from commanderbot.lib import JsonObject, JsonSerializable

SelfType = TypeVar("SelfType")


class AutomodEntity(Protocol):
    """Base interface for automod triggers, conditions, and actions."""

    @classmethod
    def from_data(cls: Type[SelfType], data: JsonObject) -> SelfType:
        """Create an entity from data."""


# @implements AutomodEntity
@dataclass
class AutomodEntityBase(JsonSerializable):
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

    @classmethod
    def get_type_string(cls) -> str:
        """Override this if the external type field requires special handling."""
        if not cls.default_module_prefix:
            raise ValueError(
                f"Subclass of {AutomodEntityBase.__name__} lacks a"
                + " `default_module_prefix`"
            )
        default_check = f"{cls.default_module_prefix}."
        full_type = cls.__module__
        if full_type.startswith(default_check):
            short_type = full_type[len(default_check) :]
            return short_type
        return full_type

    # @implements JsonSerializable
    def to_json(self) -> Any:
        # We use a custom implementation to include `type` at serialization-time only.
        type_str = self.get_type_string()
        data = dict(type=type_str)
        data.update(self.__dict__)
        return data


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
    # deserialize the entity
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
