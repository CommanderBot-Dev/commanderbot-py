from dataclasses import dataclass
from typing import Any

from commanderbot.ext.automod import events
from commanderbot.ext.automod.trigger import Trigger
from commanderbot.ext.automod.triggers.message import Message


@dataclass
class MessageDeleted(Message):
    """
    Fires when an `on_message_delete` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_message_delete
    """

    event_types = (events.MessageDeleted,)


def create_trigger(data: Any) -> Trigger:
    return MessageDeleted.from_data(data)
