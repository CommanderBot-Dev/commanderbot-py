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

    def ignore_by_includes(self, channel: TextChannel | Thread) -> bool:
        # If includes are not defined, nothing is ignored.
        if not self.include:
            return False

        # TODO Should we add extra logic for categories too? #enhance

        # If the channel is a thread, apply some additional containment logic.
        if isinstance(channel, Thread):
            # If the thread has a parent channel (it should), check that first.
            if parent_channel := channel.parent:
                # If the parent channel is included, ignore the thread only if it's
                # explicitly excluded.
                if parent_channel.id in self.include:
                    return channel.id in self.exclude

        # Otherwise, ignore the channel if and only if it's not included.
        return channel.id not in self.include

    def ignore_by_excludes(self, channel: TextChannel | Thread) -> bool:
        # Ignore channels that are excluded, if any.
        if not self.exclude:
            return False

        # TODO Should we add extra logic for categories too? #enhance

        # If the channel is a thread, apply some additional containment logic.
        if isinstance(channel, Thread):
            # If the thread has a parent channel (it should), check that first.
            if parent_channel := channel.parent:
                # If the parent channel is excluded, ignore the thread only if it's
                # not explicitly included.
                if parent_channel.id in self.exclude:
                    return channel.id not in self.include

        return channel.id in self.exclude

    def ignore(self, channel: Optional[TextChannel | Thread]) -> bool:
        """Determine whether to ignore the channel."""
        # If there's no channel, there's nothing to ignore.
        if channel is None:
            return False

        # Otherwise, check based on includes and excludes.
        return self.ignore_by_includes(channel) or self.ignore_by_excludes(channel)
