from dataclasses import dataclass
from typing import List, Optional, Type, TypeVar

from discord import Member, Message, Role, User

from commanderbot.ext.automod import events
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.automod_trigger import AutomodTrigger, AutomodTriggerBase
from commanderbot.lib import ChannelsGuard, JsonObject, RolesGuard

ST = TypeVar("ST")


@dataclass
class MentionsRemovedFromMessage(AutomodTriggerBase):
    """
    Fires when mentions are removed from a message.

    This triggers listens for `on_message_edit` and `on_message_delete` events, and uses
    different logic based on which type of event was received.

    This can be used for detecting suspected ghost pings.

    Attributes
    ----------
    channels
        The channels to match against. If empty, all channels will match.
    author_roles
        The author roles to match against. If empty, all roles will match.
    victom_roles
        The victom roles to match against. If empty, all roles will match.
    """

    event_types = (events.MessageEdited, events.MessageDeleted)

    channels: Optional[ChannelsGuard] = None
    author_roles: Optional[RolesGuard] = None
    victim_roles: Optional[RolesGuard] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        channels = ChannelsGuard.from_field_optional(data, "channels")
        author_roles = RolesGuard.from_field_optional(data, "author_roles")
        victim_roles = RolesGuard.from_field_optional(data, "victim_roles")
        return cls(
            description=data.get("description"),
            channels=channels,
            author_roles=author_roles,
            victim_roles=victim_roles,
        )

    def ignore(self, event: AutomodEvent) -> bool:
        # Make sure we care about the channel.
        if self.channels and self.channels.ignore(event.channel):
            return True

        # Make sure we care about the author.
        if self.author_roles and self.author_roles.ignore(event.author):
            return True

        # We want to preserve the order of mentions.
        removed_user_mentions: List[User | Member] = []
        removed_role_mentions: List[Role] = []

        # If the message was edited, check for mentions that were present in the message
        # only prior to editing.
        if isinstance(event, events.MessageEdited):
            # Check for removed user mentions.
            after_user_mention_ids = set(user.id for user in event._after.mentions)
            for mentioned_user in event._before.mentions:
                if mentioned_user.id not in after_user_mention_ids:
                    removed_user_mentions.append(mentioned_user)

            # Check for removed role mentions.
            after_role_mention_ids = set(role.id for role in event._after.role_mentions)
            for mentioned_role in event._before.role_mentions:
                if mentioned_role.id not in after_role_mention_ids:
                    removed_role_mentions.append(mentioned_role)

        # If the message was deleted, check for any mentions at all.
        elif isinstance(event, events.MessageDeleted):
            # Check for removed user mentions.
            deleted_user_mentions = event.message.mentions
            removed_user_mentions += deleted_user_mentions

            # Check for removed role mentions.
            deleted_role_mentions = event.message.role_mentions
            removed_role_mentions += deleted_role_mentions

            # Check if the message was a reply.
            if reference := event.message.reference:
                if isinstance(resolved := reference.resolved, Message):
                    removed_user_mentions.append(resolved.author)

        # Remove any excluded mentions.
        if self.victim_roles:
            removed_user_mentions = self.victim_roles.filter_members(
                removed_user_mentions
            )
            removed_role_mentions = self.victim_roles.filter_roles(
                removed_role_mentions
            )

        # Build removed user mention fields, if any.
        if removed_user_mentions:
            event.set_metadata(
                "removed_user_mentions",
                " ".join(user.mention for user in removed_user_mentions),
            )
            event.set_metadata(
                "removed_user_mention_names",
                " ".join(f"`{user}`" for user in removed_user_mentions),
            )

        # Build removed role mention fields, if any.
        if removed_role_mentions:
            event.set_metadata(
                "removed_role_mentions",
                " ".join(role.mention for role in removed_role_mentions),
            )
            event.set_metadata(
                "removed_role_mention_names",
                " ".join(f"`{role}`" for role in removed_role_mentions),
            )

        # If there were removed mentions of any kind, build fields and don't ignore.
        removed_mentions = list((*removed_user_mentions, *removed_role_mentions))
        if removed_mentions:
            event.set_metadata(
                "removed_mentions",
                " ".join(thing.mention for thing in removed_mentions),
            )
            event.set_metadata(
                "removed_mention_names",
                " ".join(f"`{thing}`" for thing in removed_mentions),
            )
            return False

        # If there were no removed mentions, ignore.
        return True


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return MentionsRemovedFromMessage.from_data(data)
