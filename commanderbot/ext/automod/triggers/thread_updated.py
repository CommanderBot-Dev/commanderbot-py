from dataclasses import dataclass
from typing import Any

from commanderbot.ext.automod import events
from commanderbot.ext.automod.trigger import Trigger
from commanderbot.ext.automod.triggers.abc.thread_base import ThreadBase


@dataclass
class ThreadUpdated(ThreadBase):
    """
    Fires when an `on_thread_update` event is received.

    See: https://discordpy.readthedocs.io/en/master/api.html#discord.on_thread_update

    Attributes
    ----------
    parent_channels
        The parent channels to match against. If empty, all channels will match.
    """

    event_types = (events.ThreadUpdated,)


def create_trigger(data: Any) -> Trigger:
    return ThreadUpdated.from_data(data)
