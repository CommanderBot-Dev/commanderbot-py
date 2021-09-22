from dataclasses import dataclass

from commanderbot.ext.automod import events
from commanderbot.ext.automod.trigger import Trigger
from commanderbot.ext.automod.triggers.message import Message
from commanderbot.lib import JsonObject


@dataclass
class MessageEdited(Message):
    """
    Fires when an `on_message_edit` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_message_edit
    """

    event_types = (events.MessageEdited,)


def create_trigger(data: JsonObject) -> Trigger:
    return MessageEdited.from_data(data)
