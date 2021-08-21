from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.ext.automod.automod_trigger import AutomodTriggerBase
from commanderbot_ext.lib import ChannelsGuard, JsonObject, ReactionsGuard, RolesGuard

ST = TypeVar("ST")


@dataclass
class _ReactionBase(AutomodTriggerBase):
    event_types = ()

    reactions: Optional[ReactionsGuard] = None
    channels: Optional[ChannelsGuard] = None
    author_roles: Optional[RolesGuard] = None
    actor_roles: Optional[RolesGuard] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        reactions = ReactionsGuard.from_field_optional(data, "reactions")
        channels = ChannelsGuard.from_field_optional(data, "channels")
        author_roles = RolesGuard.from_field_optional(data, "author_roles")
        actor_roles = RolesGuard.from_field_optional(data, "actor_roles")
        return cls(
            reactions=reactions,
            description=data.get("description"),
            channels=channels,
            author_roles=author_roles,
            actor_roles=actor_roles,
        )

    def ignore_by_reaction(self, event: AutomodEvent) -> bool:
        if self.reactions is None:
            return False
        return self.reactions.ignore(event.reaction)

    def ignore_by_channel(self, event: AutomodEvent) -> bool:
        if self.channels is None:
            return False
        return self.channels.ignore(event.channel)

    def ignore_by_author_role(self, event: AutomodEvent) -> bool:
        if self.author_roles is None:
            return False
        return self.author_roles.ignore(event.author)

    def ignore_by_actor_role(self, event: AutomodEvent) -> bool:
        if self.actor_roles is None:
            return False
        return self.actor_roles.ignore(event.actor)

    def ignore(self, event: AutomodEvent) -> bool:
        return (
            self.ignore_by_reaction(event)
            or self.ignore_by_channel(event)
            or self.ignore_by_author_role(event)
            or self.ignore_by_actor_role(event)
        )
