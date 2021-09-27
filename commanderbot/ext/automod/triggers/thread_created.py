from dataclasses import dataclass
from typing import Any, Dict, Optional

from commanderbot.ext.automod import events
from commanderbot.ext.automod.trigger import Trigger, TriggerBase
from commanderbot.lib import ChannelsGuard, JsonObject


@dataclass
class ThreadCreated(TriggerBase):
    """
    Fires when an `on_thread_join` event is received without already being a member.

    See: https://discordpy.readthedocs.io/en/master/api.html#discord.on_thread_join

    Attributes
    ----------
    parent_channels
        The parent channels to match against. If empty, all channels will match.
    """

    event_types = (events.ThreadCreated,)

    parent_channels: Optional[ChannelsGuard] = None

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        parent_channels = ChannelsGuard.from_field_optional(data, "parent_channels")
        return dict(
            parent_channels=parent_channels,
        )

    def ignore(self, event: events.ThreadCreated) -> bool:
        # If no parent channels are defined, don't ignore the thread.
        if self.parent_channels is None:
            return False

        # If the thread has no parent, ignore it.
        if not event.thread.parent:
            return True

        # Otherwise, ignore the thread according to its parent.
        return self.parent_channels.ignore(event.thread.parent)


def create_trigger(data: JsonObject) -> Trigger:
    return ThreadCreated.from_data(data)
