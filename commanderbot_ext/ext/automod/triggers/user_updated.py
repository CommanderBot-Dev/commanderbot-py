from dataclasses import dataclass

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_trigger import (
    AutomodTrigger,
    AutomodTriggerBase,
)
from commanderbot_ext.lib import JsonObject


@dataclass
class UserUpdated(AutomodTriggerBase):
    """
    Fires when an `on_user_update` event is received.

    This occurs when one or more of the following things change:
    - avatar
    - username
    - discriminator

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_user_update
    """

    event_types = (events.UserUpdated,)


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return UserUpdated.from_data(data)
