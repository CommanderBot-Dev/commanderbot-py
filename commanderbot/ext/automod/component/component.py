from typing import ClassVar, Protocol

from commanderbot.ext.automod.node.node import Node

__all__ = ("Component",)


class Component(Node, Protocol):
    """
    Base interface for automod components.

    Components are nodes that inherit functionality based on their type. For example:
    buckets, triggers, conditions, and actions are all components and all require a
    pre-determined `type` to function.

    A componenet's `type` generally corresponds to a module that is used in the
    de/serialization process to construct the underlying object dynamically at runtime.

    Note that while rules are nodes, they are not components.
    """

    default_module_prefix: ClassVar[str]
    module_function_name: ClassVar[str]
