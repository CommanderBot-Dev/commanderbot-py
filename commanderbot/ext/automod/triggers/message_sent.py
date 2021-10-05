from dataclasses import dataclass
from typing import Any

from commanderbot.ext.automod import events
from commanderbot.ext.automod.trigger import Trigger
from commanderbot.ext.automod.triggers.message import Message


@dataclass
class MessageSent(Message):
    """
    Fires when an `on_message` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_message
    """

    event_types = (events.MessageSent,)


def create_trigger(data: Any) -> Trigger:
    return MessageSent.from_data(data)
