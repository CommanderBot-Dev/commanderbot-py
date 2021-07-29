from dataclasses import dataclass

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_trigger import AutomodTrigger
from commanderbot_ext.ext.automod.triggers.message import Message
from commanderbot_ext.lib import JsonObject


@dataclass
class MessageDeleted(Message):
    event_types = (events.MessageDeleted,)


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return MessageDeleted.from_data(data)
