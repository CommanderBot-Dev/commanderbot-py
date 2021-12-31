from dataclasses import dataclass, field
from typing import Optional, Set

from discord import TextChannel, Thread

from commanderbot.lib.from_data_mixin import FromDataMixin

__all__ = ("ChannelTypesGuard",)


THREAD_TYPES = {
    TextChannel: "text",
    Thread: "thread",
}


@dataclass
class ChannelTypesGuard(FromDataMixin):
    """
    Check whether a channel is of a certain type.

    Attributes
    ----------
    include
        The channel types to include. A channel will match if it's one of these types.
    exclude
        The channel types to exclude. A channel will match if it's not one of these
        types.
    """

    include: Set[str] = field(default_factory=set)
    exclude: Set[str] = field(default_factory=set)

    @classmethod
    def try_from_data(cls, data):
        if isinstance(data, dict):
            return cls(
                include=set(data.get("include", [])),
                exclude=set(data.get("exclude", [])),
            )
        elif isinstance(data, list):
            return cls(include=set(data))

    def ignore_by_includes(self, type_name: str) -> bool:
        if not self.include:
            return False
        return type_name not in self.include

    def ignore_by_excludes(self, type_name: str) -> bool:
        if not self.exclude:
            return False
        return type_name in self.exclude

    def ignore(self, channel: Optional[TextChannel | Thread]) -> bool:
        """Determine whether to ignore the channel based on its type."""
        if channel is None:
            return False
        channel_type = type(channel)
        type_name = THREAD_TYPES.get(channel_type, "other")
        return self.ignore_by_includes(type_name) or self.ignore_by_excludes(type_name)
