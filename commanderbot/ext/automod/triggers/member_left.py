from dataclasses import dataclass

from commanderbot.ext.automod import events
from commanderbot.ext.automod.trigger import Trigger, TriggerBase
from commanderbot.lib import JsonObject


@dataclass
class MemberLeft(TriggerBase):
    """
    Fires when an `on_member_remove` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_remove
    """

    event_types = (events.MemberLeft,)


def create_trigger(data: JsonObject) -> Trigger:
    return MemberLeft.from_data(data)
