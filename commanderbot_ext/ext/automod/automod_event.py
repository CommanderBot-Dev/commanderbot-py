from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional, Protocol, Tuple, cast

from discord import Member, TextChannel, User
from discord.ext.commands import Bot

from commanderbot_ext.lib import ShallowFormatter
from commanderbot_ext.lib.types import TextMessage, TextReaction


class AutomodEvent(Protocol):
    bot: Bot

    @property
    def channel(self) -> Optional[TextChannel]:
        """Return the relevant channel, if any."""

    @property
    def message(self) -> Optional[TextMessage]:
        """Return the relevant message, if any."""

    @property
    def reaction(self) -> Optional[TextReaction]:
        """Return the relevant reaction, if any."""

    @property
    def author(self) -> Optional[Member]:
        """Return the relevant author, if any."""

    @property
    def actor(self) -> Optional[Member]:
        """Return the acting user, if any."""

    @property
    def member(self) -> Optional[Member]:
        """Return the member-in-question, if any."""

    @property
    def user(self) -> Optional[User]:
        """Return the user-in-question, if any."""

    def set_metadata(self, key: str, value: Any):
        """Attach metadata to the event."""

    def remove_metadata(self, key: str):
        """Remove metadata from the event."""

    def format_content(self, content: str, *, unsafe: bool = False) -> str:
        """Format a string with event data."""


# @implements AutomodEvent
@dataclass
class AutomodEventBase:
    bot: Bot

    _metadata: Dict[str, Any] = field(init=False, default_factory=dict)

    def __init__(
        self,
        bot: Bot,
        **data: Dict[str, Any],
    ) -> None:
        self.bot = bot
        self._metadata = {}

    @property
    def channel(self) -> Optional[TextChannel]:
        return None

    @property
    def message(self) -> Optional[TextMessage]:
        return None

    @property
    def reaction(self) -> Optional[TextReaction]:
        return None

    @property
    def author(self) -> Optional[Member]:
        return None

    @property
    def actor(self) -> Optional[Member]:
        return None

    @property
    def member(self) -> Optional[Member]:
        return None

    @property
    def user(self) -> Optional[User]:
        return cast(User, self.member)

    def set_metadata(self, key: str, value: Any):
        self._metadata[key] = value

    def remove_metadata(self, key: str):
        del self._metadata[key]

    def format_content(self, content: str, *, unsafe: bool = False) -> str:
        # NOTE Beware of untrusted format strings!
        # Instead of providing a handful of library objects with arbitrary (and
        # potentially sensitive) data to the format string, we build a flattened set of
        # arguments and pass them to a safe formatter. Pass `unsafe=True` to explicitly
        # enable unsafe formatting for things like field access.
        format_args = self._get_format_args(unsafe)
        if unsafe:
            return content.format_map(format_args)
        return ShallowFormatter().format(content, **format_args)

    def _get_format_args(self, unsafe: bool = False) -> Dict[str, Any]:
        if unsafe:
            return self._get_unsafe_format_args()
        return self._get_safe_format_args()

    def _get_unsafe_format_args(self) -> Dict[str, Any]:
        format_args = self._get_safe_format_args()
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

    def _get_safe_format_args(self) -> Dict[str, Any]:
        return {k: v for k, v in self._yield_safe_format_args()}

    def _yield_safe_format_args(self) -> Iterable[Tuple[str, Any]]:
        if self.channel is not None:
            yield "channel_id", self.channel.id,
            yield "channel_name", self.channel.name,
            yield "channel_mention", self.channel.mention,
        if self.message is not None:
            yield "message_id", self.message.id
            yield "message_content", self.message.content
            yield "message_clean_content", self.message.clean_content
            yield "message_jump_url", self.message.jump_url
        if self.reaction is not None:
            yield "reaction_emoji", self.reaction.emoji
            yield "reaction_count", self.reaction.count
        if self.author is not None:
            yield from self._get_safe_member_args("author", self.author)
        if self.actor is not None:
            yield from self._get_safe_member_args("actor", self.actor)
        if self.member is not None:
            yield from self._get_safe_member_args("member", self.member)
        yield from self._get_safe_metadata_args()

    def _get_safe_member_args(
        self, prefix: str, member: Member
    ) -> Iterable[Tuple[str, Any]]:
        yield f"{prefix}_id", member.id
        yield f"{prefix}_name", member.name
        yield f"{prefix}_discriminator", member.discriminator
        yield f"{prefix}_mention", member.mention
        yield f"{prefix}_display_name", member.display_name

    def _get_safe_metadata_args(self) -> Iterable[Tuple[str, Any]]:
        for k, v in self._metadata.items():
            if type(v) in (bool, int, float, str):
                yield k, v
