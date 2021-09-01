from dataclasses import dataclass, field
from typing import Optional, Set

from discord import TextChannel, Thread

from commanderbot.lib.from_data_mixin import FromDataMixin
from commanderbot.lib.types import ChannelID

__all__ = ("ChannelsGuard",)


@dataclass
class ChannelsGuard(FromDataMixin):
    """
    Check whether a channel matches a set of channels.

    Attributes
    ----------
    include
        The channels to include. A channel will match if it is in this set.
    exclude
        The channels to exclude. A channel will match if it is not in this set.
    """

    include: Set[ChannelID] = field(default_factory=set)
    exclude: Set[ChannelID] = field(default_factory=set)

    @classmethod
    def try_from_data(cls, data):
        if isinstance(data, dict):
            return cls(
                include=set(data.get("include", [])),
                exclude=set(data.get("exclude", [])),
            )
        elif isinstance(data, list):
            return cls(include=set(data))

    def get_root_channel(self, channel: TextChannel | Thread) -> Optional[TextChannel]:
        if isinstance(channel, TextChannel):
            return channel
        return channel.parent

    def ignore_by_includes(self, channel: TextChannel | Thread) -> bool:
        # Ignore channels that are not included, if any.
        if not self.include:
            return False
        if root_channel := self.get_root_channel(channel):
            return root_channel.id not in self.include
        return False

    def ignore_by_excludes(self, channel: TextChannel | Thread) -> bool:
        # Ignore channels that are excluded, if any.
        if not self.exclude:
            return False
        if root_channel := self.get_root_channel(channel):
            return root_channel.id in self.exclude
        return False

    def ignore(self, channel: Optional[TextChannel | Thread]) -> bool:
        """Determine whether to ignore the channel."""
        if channel is None:
            return False
        return self.ignore_by_includes(channel) or self.ignore_by_excludes(channel)
