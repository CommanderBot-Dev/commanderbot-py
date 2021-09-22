from dataclasses import dataclass

from commanderbot.ext.automod import events
from commanderbot.ext.automod.trigger import Trigger, TriggerBase
from commanderbot.lib import JsonObject


@dataclass
class MemberJoined(TriggerBase):
    """
    Fires when an `on_member_join` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_join
    """

    event_types = (events.MemberJoined,)


def create_trigger(data: JsonObject) -> Trigger:
    return MemberJoined.from_data(data)
