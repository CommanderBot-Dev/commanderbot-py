from dataclasses import dataclass
from typing import ClassVar

from commanderbot.ext.automod import actions
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.component import ComponentBase

__all__ = ("ActionBase",)


# @implements ComponentBase
# @implements Action
@dataclass
class ActionBase(ComponentBase):
    # @implements ComponentBase
    default_module_prefix: ClassVar[str] = actions.__name__

    # @implements ComponentBase
    module_function_name: ClassVar[str] = "create_action"

    # @implements Action
    async def apply(self, event: AutomodEvent):
        """Override this to apply the action."""
