from dataclasses import dataclass, field
from typing import Optional, Set

from discord import TextChannel

from commanderbot_ext.lib.from_data_mixin import FromDataMixin
from commanderbot_ext.lib.types import ChannelID

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

    def ignore_by_includes(self, channel: TextChannel) -> bool:
        # Ignore channels that are not included, if any.
        if not self.include:
            return False
        return channel.id not in self.include

    def ignore_by_excludes(self, channel: TextChannel) -> bool:
        # Ignore channels that are excluded, if any.
        if not self.exclude:
            return False
        return channel.id in self.exclude

    def ignore(self, channel: Optional[TextChannel]) -> bool:
        """Determine whether to ignore the channel."""
        if channel is None:
            return False
        return self.ignore_by_includes(channel) or self.ignore_by_excludes(channel)
