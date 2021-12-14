from dataclasses import dataclass, field
from logging import Logger
from typing import Any, ClassVar, Dict, Iterable, Optional, Tuple, Type, cast

from discord import Member, TextChannel, Thread, User
from discord.ext.commands import Bot

from commanderbot.ext.automod.event.event_state import EventState
from commanderbot.lib import ShallowFormatter, TextMessage, TextReaction, ValueFormatter
from commanderbot.lib.utils import yield_member_date_fields

__all__ = ("EventBase",)


# @implements Event
@dataclass
class EventBase:
    # @implements Event
    state: EventState
    bot: Bot
    log: Logger

    _metadata: Dict[str, Any] = field(init=False, default_factory=dict)

    SAFE_TYPES: ClassVar[Tuple[Type, ...]] = (bool, int, float, str)

    def __init__(
        self,
        bot: Bot,
        log: Logger,
        **data: Dict[str, Any],
    ) -> None:
        self.bot = bot
        self.log = log
        self._metadata = {}

    # @implements Event
    @property
    def channel(self) -> Optional[TextChannel | Thread]:
        return None

    # @implements Event
    @property
    def thread(self) -> Optional[Thread]:
        if isinstance(self.channel, Thread):
            return self.channel

    # @implements Event
    @property
    def message(self) -> Optional[TextMessage]:
        return None

    # @implements Event
    @property
    def reaction(self) -> Optional[TextReaction]:
        return None

    # @implements Event
    @property
    def author(self) -> Optional[Member]:
        return None

    # @implements Event
    @property
    def actor(self) -> Optional[Member]:
        return None

    # @implements Event
    @property
    def member(self) -> Optional[Member]:
        return None

    # @implements Event
    @property
    def user(self) -> Optional[User]:
        return cast(User, self.member)

    # @implements Event
    def set_metadata(self, key: str, value: Any):
        self._metadata[key] = value

    # @implements Event
    def remove_metadata(self, key: str):
        del self._metadata[key]

    # @implements Event
    def get_fields(self, unsafe: bool = False) -> Dict[str, Any]:
        if unsafe:
            return self._get_fields_unsafe()
        return self._get_fields_safe()

    # @implements Event
    def format_content(self, content: str, *, unsafe: bool = False) -> str:
        # NOTE Beware of untrusted format strings!
        # Instead of providing a handful of library objects with arbitrary (and
        # potentially sensitive) data to the format string, we build a flattened set of
        # arguments and pass them to a safe formatter. Pass `unsafe=True` to explicitly
        # enable unsafe formatting for things like field access.
        fields = self.get_fields(unsafe)
        if unsafe:
            return content.format_map(fields)
        return ShallowFormatter().format(content, **fields)

    def _get_fields_unsafe(self) -> Dict[str, Any]:
        format_args = self._get_fields_safe()
        format_args.update(
            channel=self.channel,
            message=self.message,
            reaction=self.reaction,
            author=self.author,
            actor=self.actor,
            member=self.member,
        )
        format_args.update(self._metadata)
        return format_args

    def _get_fields_safe(self) -> Dict[str, Any]:
        return {k: v for k, v in self._yield_safe_fields()}

    def _is_value_safe(self, v: Any) -> bool:
        return (type(v) in self.SAFE_TYPES) or (
            isinstance(v, ValueFormatter) and (type(v.value) in self.SAFE_TYPES)
        )

    def _yield_safe_fields(self) -> Iterable[Tuple[str, Any]]:
        if self.channel is not None:
            yield "channel_id", self.channel.id,
            yield "channel_name", self.channel.name,
            yield "channel_mention", self.channel.mention,
        if self.thread is not None:
            yield "thread_id", self.thread.id,
            yield "thread_name", self.thread.name,
            yield "thread_mention", self.thread.mention,
            yield "thread_archived", self.thread.archived,
            yield "thread_locked", self.thread.locked,
            yield "thread_slowmode_delay", self.thread.slowmode_delay,
            yield "thread_auto_archive_duration", self.thread.auto_archive_duration,
            if (thread_owner := self.thread.owner) is not None:
                yield from self._yield_safe_member_fields("thread_owner", thread_owner)
        if self.message is not None:
            yield "message_id", self.message.id
            yield "message_content", self.message.content
            yield "message_clean_content", self.message.clean_content
            yield "message_jump_url", self.message.jump_url
        if self.reaction is not None:
            yield "reaction_emoji", self.reaction.emoji
            yield "reaction_count", self.reaction.count
        if self.author is not None:
            yield from self._yield_safe_member_fields("author", self.author)
        if self.actor is not None:
            yield from self._yield_safe_member_fields("actor", self.actor)
        if self.member is not None:
            yield from self._yield_safe_member_fields("member", self.member)
        if self.user is not None:
            yield from self._yield_safe_user_fields("user", self.user)
        for k, v in self._yield_extra_fields():
            if self._is_value_safe(v):
                yield k, v
        for k, v in self._yield_metadata_fields():
            if self._is_value_safe(v):
                yield k, v

    def _yield_safe_member_fields(
        self, prefix: str, member: Member
    ) -> Iterable[Tuple[str, Any]]:
        yield from self._yield_safe_user_fields(prefix, cast(User, member))
        yield f"{prefix}_nick", member.nick
        yield from yield_member_date_fields(prefix, member)

    def _yield_safe_user_fields(
        self, prefix: str, user: User
    ) -> Iterable[Tuple[str, Any]]:
        yield f"{prefix}_id", user.id
        yield f"{prefix}_name", f"{user}"
        yield f"{prefix}_username", user.name
        yield f"{prefix}_discriminator", user.discriminator
        yield f"{prefix}_mention", user.mention
        yield f"{prefix}_display_name", user.display_name

    def _yield_extra_fields(self) -> Iterable[Tuple[str, Any]]:
        """Override this to provide additional fields based on the event type."""
        if False:
            yield

    def _yield_metadata_fields(self) -> Iterable[Tuple[str, Any]]:
        for k, v in self._metadata.items():
            yield k, v
