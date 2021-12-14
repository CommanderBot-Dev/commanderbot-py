from dataclasses import dataclass
from typing import Any

from commanderbot.ext.automod import events
from commanderbot.ext.automod.trigger import Trigger, TriggerBase


@dataclass
class MemberJoined(TriggerBase):
    """
    Fires when an `on_member_join` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_join
    """

    event_types = (events.MemberJoined,)


def create_trigger(data: Any) -> Trigger:
    return MemberJoined.from_data(data)
