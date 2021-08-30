from dataclasses import dataclass

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_trigger import AutomodTrigger
from commanderbot_ext.ext.automod.triggers.message import Message
from commanderbot_ext.lib import JsonObject


@dataclass
class MessageEdited(Message):
    """
    Fires when an `on_message_edit` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_message_edit
    """

    event_types = (events.MessageEdited,)


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return MessageEdited.from_data(data)
