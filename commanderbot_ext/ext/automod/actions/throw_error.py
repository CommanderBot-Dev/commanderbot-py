from dataclasses import dataclass

from commanderbot_ext.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject


@dataclass
class ThrowError(AutomodActionBase):
    error: str

    async def apply(self, event: AutomodEvent):
        raise Exception(self.error)


def create_action(data: JsonObject) -> AutomodAction:
    return ThrowError.from_data(data)
