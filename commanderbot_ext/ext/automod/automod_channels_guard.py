from dataclasses import dataclass, field
from typing import Set, Type, TypeVar

from discord import TextChannel

from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import ChannelID, JsonObject

ST = TypeVar("ST")


@dataclass
class AutomodChannelsGuard:
    include: Set[ChannelID] = field(default_factory=set)
    exclude: Set[ChannelID] = field(default_factory=set)

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        return cls(
            include=set(data.get("include", [])),
            exclude=set(data.get("exclude", [])),
        )

    def ignore_by_includes(self, channel: TextChannel) -> bool:
        # If `include` channels are configured, ignore any channels outside of them.
        return bool(self.include) and (channel.id not in self.include)

    def ignore_by_excludes(self, channel: TextChannel) -> bool:
        # If `exclude` channels are configured, ignore any channels inside of them.
        return bool(self.exclude) and (channel.id in self.exclude)

    def ignore(self, event: AutomodEvent) -> bool:
        if channel := event.channel:
            return self.ignore_by_includes(channel) or self.ignore_by_excludes(channel)
        return True
