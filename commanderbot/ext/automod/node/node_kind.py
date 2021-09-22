from dataclasses import dataclass
from enum import Enum
from typing import Generic, Type, TypeVar

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


NT = TypeVar("NT", bound=Node)


class NodeKind(Enum):
    @dataclass
    class _Value(Generic[NT]):
        plural: str
        singular: str
        node_type: Type[NT]

    RULE = _Value("rule", "rules", Rule)
    BUCKET = _Value("bucket", "buckets", Bucket)
    TRIGGER = _Value("trigger", "triggers", Trigger)
    CONDITION = _Value("condition", "conditions", Condition)
    ACTION = _Value("action", "actions", Action)

    def __str__(self) -> str:
        return self.value.singular

    @property
    def plural(self) -> str:
        return self.value.plural

    @property
    def singular(self) -> str:
        return self.value.singular

    @property
    def node_type(self) -> Type[NT]:
        return self.value.node_type


class NodeKindConverter:
    async def convert(self, ctx: Context, argument: str) -> NodeKind:
        try:
            return NodeKind[argument]
        except:
            pass

        try:
            return NodeKind[argument.upper()]
        except:
            pass

        raise ResponsiveException(f"No such `{NodeKind.__name__}`: `{argument}`")
