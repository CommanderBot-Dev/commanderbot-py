from dataclasses import dataclass
from typing import ClassVar

from commanderbot.ext.automod import conditions
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.component import ComponentBase

__all__ = ("ConditionBase",)


# @implements Condition
@dataclass
class ConditionBase(ComponentBase):
    # @implements ComponentBase
    default_module_prefix: ClassVar[str] = conditions.__name__
    
    # @implements ComponentBase
    module_function_name: ClassVar[str] = "create_condition"

    async def check(self, event: AutomodEvent) -> bool:
        """Override this to check whether the condition passes."""
        return False
