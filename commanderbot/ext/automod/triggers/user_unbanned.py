from dataclasses import dataclass

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_trigger import (
    AutomodTrigger,
    AutomodTriggerBase,
)
from commanderbot_ext.lib import JsonObject


@dataclass
class UserUnbanned(AutomodTriggerBase):
    """
    Fires when an `on_member_unban` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_unban
    """

    event_types = (events.UserUnbanned,)


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return UserUnbanned.from_data(data)
