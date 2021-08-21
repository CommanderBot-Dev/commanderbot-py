from dataclasses import dataclass

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_trigger import (
    AutomodTrigger,
    AutomodTriggerBase,
)
from commanderbot_ext.lib import JsonObject


@dataclass
class MemberBanned(AutomodTriggerBase):
    """
    Fires when an `on_member_ban` event is received for a guild member.

    Note that this only occurs when the user was a member of the guild at the time of
    being banned.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_ban
    """

    event_types = (events.MemberBanned,)


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return MemberBanned.from_data(data)
