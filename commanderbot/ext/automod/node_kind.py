from dataclasses import dataclass
from typing import Dict, Generic, Type, TypeVar

from discord.ext.commands import Context

from commanderbot.ext.automod.node.node import Node
from commanderbot.lib.responsive_exception import ResponsiveException

__all__ = (
    "NodeKind",
    "NodeKindConverter",
)


NT = TypeVar("NT", bound=Node)


@dataclass
class NodeKind(Generic[NT]):
    node_type: Type[NT]
    singular: str
    plural: str

    def __str__(self) -> str:
        return self.singular


class NodeKindConverter:
    def __init__(self):
        self._node_kinds: Dict[str, NodeKind] = {}

    @property
    def node_kinds(self) -> Dict[str, NodeKind]:
        if not self._node_kinds:
            from commanderbot.ext.automod.action.action import Action
            from commanderbot.ext.automod.bucket.bucket import Bucket
            from commanderbot.ext.automod.condition.condition import Condition
            from commanderbot.ext.automod.rule.rule import Rule
            from commanderbot.ext.automod.trigger.trigger import Trigger

            self._node_kinds = {
                "rule": NodeKind(Rule, "rule", "rules"),
                "bucket": NodeKind(Bucket, "bucket", "buckets"),
                "trigger": NodeKind(Trigger, "trigger", "triggers"),
                "condition": NodeKind(Condition, "condition", "conditions"),
                "action": NodeKind(Action, "action", "actions"),
            }

        return self._node_kinds

    async def convert(self, ctx: Context, argument: str) -> NodeKind:
        try:
            return self.node_kinds[argument]
        except:
            pass

        node_kinds = [node_kind for node_kind in self.node_kinds.values()]
        node_kinds_str = " ".join(f"`{node_kind}`" for node_kind in node_kinds)
        raise ResponsiveException(
            f"No such node type `{argument}`" + f" (must be one of: {node_kinds_str})"
        )
