from dataclasses import dataclass
from typing import Any, Generic, Type, TypeVar

from commanderbot.ext.automod.component.component import Component
from commanderbot.ext.automod.node import NodeCollection
from commanderbot.ext.automod.utils import deserialize_module_object

ST = TypeVar("ST", bound="ComponentCollection")
CT = TypeVar("CT", bound=Component)


# @abstract
@dataclass(init=False)
class ComponentCollection(NodeCollection[CT], Generic[CT]):
    """A collection of components with the same base type."""

    # @overrides NodeCollection
    @classmethod
    def build_node_from_data(cls: Type[ST], data: Any) -> CT:
        # Instead of just constructing objects out of the base type, actually look
        # at the `type` field and build them dynamically from modules.
        component_type: Type[CT] = cls.node_type
        component = deserialize_module_object(
            data=data,
            default_module_prefix=component_type.default_module_prefix,
            function_name=component_type.module_function_name,
        )
        assert isinstance(component, component_type)
        return component
