from dataclasses import dataclass
from typing import Any

from commanderbot.ext.automod import events
from commanderbot.ext.automod.trigger import Trigger, TriggerBase


@dataclass
class UserBanned(TriggerBase):
    """
    Fires when an `on_member_ban` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_ban
    """

    event_types = (events.UserBanned,)


def create_trigger(data: Any) -> Trigger:
    return UserBanned.from_data(data)
