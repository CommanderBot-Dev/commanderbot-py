from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, TypeVar

from commanderbot.ext.automod.node.node_base import NodeBase

__all__ = ("ComponentBase",)


ST = TypeVar("ST", bound="ComponentBase")


# @implements Component
@dataclass
class ComponentBase(NodeBase):
    """
    Base implementation for automod components.

    See `Component` for a description of what components are.

    This includes logic for using the `type` field to load a python module and call one
    of its functions to deserialize the given data and create a new object.
    """

    @classmethod
    @property
    @abstractmethod
    def default_module_prefix(cls) -> str:
        ...

    @classmethod
    @property
    @abstractmethod
    def module_function_name(cls) -> str:
        ...

    @classmethod
    def get_type_string(cls) -> str:
        """Override this if the external type field requires special handling."""
        default_check = f"{cls.default_module_prefix}."
        full_type = cls.__module__
        if full_type.startswith(default_check):
            short_type = full_type[len(default_check) :]
            return short_type
        return full_type

    # @overrides ToData
    def base_fields_to_data(self) -> Optional[Dict[str, Any]]:
        # Include `type` as a base field at serialization-time only.
        type_str = self.get_type_string()
        base_fields = dict(type=type_str)
        return base_fields
