from typing import ClassVar, Type

from commanderbot.ext.automod.node import NodeRef
from commanderbot.ext.automod.rule.rule import Rule

__all__ = ("RuleRef",)


# @implements NodeRef
class RuleRef(NodeRef[Rule]):
    """A reference to a rule, by name."""

    # @implements NodeRef
    node_type: ClassVar[Type[Rule]] = Rule
