from dataclasses import dataclass

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_trigger import (
    AutomodTrigger,
    AutomodTriggerBase,
)
from commanderbot_ext.lib import JsonObject


@dataclass
class UserBanned(AutomodTriggerBase):
    """
    Fires when an `on_member_ban` event is received.

    Note that this occurs regardless of whether the user was a member of the guild at
    the time of being banned.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_ban
    """

    event_types = (events.UserBanned, events.MemberBanned)


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return UserBanned.from_data(data)