from dataclasses import dataclass
from typing import Dict, Type

from discord.ext.commands import Context

from commanderbot.ext.automod.action.action import Action
from commanderbot.ext.automod.bucket.bucket import Bucket
from commanderbot.ext.automod.condition.condition import Condition
from commanderbot.ext.automod.node.node import Node
from commanderbot.ext.automod.rule.rule import Rule
from commanderbot.ext.automod.trigger.trigger import Trigger
from commanderbot.lib.responsive_exception import ResponsiveException

__all__ = (
    "NodeKind",
    "NodeKindConverter",
)


@dataclass
class NodeKind:
    node_type: Type[Node]
    singular: str
    plural: str

    def __str__(self) -> str:
        return self.singular


rule = NodeKind(Rule, "rule", "rules")
bucket = NodeKind(Bucket, "bucket", "buckets")
trigger = NodeKind(Trigger, "trigger", "triggers")
condition = NodeKind(Condition, "condition", "conditions")
action = NodeKind(Action, "action", "actions")


NODE_KINDS: Dict[str, NodeKind] = {
    "rule": rule,
    "bucket": bucket,
    "trigger": trigger,
    "condition": condition,
    "action": action,
}


class NodeKindConverter:
    async def convert(self, ctx: Context, argument: str) -> NodeKind:
        try:
            return NODE_KINDS[argument]
        except:
            pass

        node_kinds = [node_kind for node_kind in NODE_KINDS.values()]
        node_kinds_str = " ".join(f"`{node_kind}`" for node_kind in node_kinds)
        raise ResponsiveException(
            f"No such node type `{argument}`" + f" (must be one of: {node_kinds_str})"
        )
