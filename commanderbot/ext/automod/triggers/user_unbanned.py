from dataclasses import dataclass
from typing import Any

from commanderbot.ext.automod import events
from commanderbot.ext.automod.trigger import Trigger, TriggerBase


@dataclass
class UserUnbanned(TriggerBase):
    """
    Fires when an `on_member_unban` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_unban
    """

    event_types = (events.UserUnbanned,)


def create_trigger(data: Any) -> Trigger:
    return UserUnbanned.from_data(data)
