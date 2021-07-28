from dataclasses import dataclass, field
from typing import Set, Union

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_trigger import (
    AutomodTrigger,
    AutomodTriggerBase,
)
from commanderbot_ext.lib import JsonObject
from commanderbot_ext.lib.types import ChannelID, RoleID
from commanderbot_ext.lib.utils import convert_field_values, member_roles_from


@dataclass
class Message(AutomodTriggerBase):
    EventTypes = Union[events.MessageSent, events.MessageEdited]
    event_types = (events.MessageSent, events.MessageEdited)

    channels: Set[ChannelID] = field(default_factory=set)
    not_channels: Set[ChannelID] = field(default_factory=set)

    roles: Set[RoleID] = field(default_factory=set)
    not_roles: Set[RoleID] = field(default_factory=set)

    @classmethod
    def deserialize_fields(cls, data: JsonObject) -> JsonObject:
        processed_data = data.copy()
        convert_field_values(processed_data, "channels", int, set)
        convert_field_values(processed_data, "not_channels", int, set)
        convert_field_values(processed_data, "roles", int, set)
        convert_field_values(processed_data, "not_roles", int, set)
        return processed_data

    def serialize_fields(self) -> JsonObject:
        data = self.__dict__.copy()
        convert_field_values(data, "channels", int, list, delete_empty=True)
        convert_field_values(data, "not_channels", int, list, delete_empty=True)
        convert_field_values(data, "roles", int, list, delete_empty=True)
        convert_field_values(data, "not_roles", int, list, delete_empty=True)
        return data

    def ignore_by_channels(self, event: EventTypes) -> bool:
        # If `channels` are configured, ignore any messages outside of them.
        return bool(self.channels) and (event.channel.id not in self.channels)

    def ignore_by_not_channels(self, event: EventTypes) -> bool:
        # If `not_channels` are configured, ignore any messages inside of them.
        return bool(self.not_channels) and (event.channel.id in self.not_channels)

    def ignore_by_roles(self, event: EventTypes) -> bool:
        # If `roles` are configured, ignore any messages not sent by a member.
        member_roles = member_roles_from(event.author, self.roles)
        return bool(self.roles) and not member_roles

    def ignore_by_not_roles(self, event: EventTypes) -> bool:
        # If `not_roles` are configured, ignore any messages sent by a member.
        member_roles = member_roles_from(event.author, self.not_roles)
        return bool(self.not_roles) and bool(member_roles)

    def ignore(self, event: EventTypes) -> bool:
        return (
            self.ignore_by_channels(event)
            or self.ignore_by_not_channels(event)
            or self.ignore_by_roles(event)
            or self.ignore_by_not_roles(event)
        )


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return Message.deserialize(data)
