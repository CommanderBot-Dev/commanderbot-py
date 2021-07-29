from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol

from discord import Member, Message, Reaction, TextChannel
from discord.ext.commands import Bot


class AutomodEvent(Protocol):
    bot: Bot

    @property
    def channel(self) -> Optional[TextChannel]:
        """Return the relevant channel, if any."""

    @property
    def message(self) -> Optional[Message]:
        """Return the relevant message, if any."""

    @property
    def reaction(self) -> Optional[Reaction]:
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

    def set_metadata(self, key: str, value: Any):
        """Attach metadata to the event."""

    def remove_metadata(self, key: str):
        """Remove metadata from the event."""

    def format_content(self, content: str) -> str:
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
    def message(self) -> Optional[Message]:
        return None

    @property
    def reaction(self) -> Optional[Reaction]:
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

    def set_metadata(self, key: str, value: Any):
        self._metadata[key] = value

    def remove_metadata(self, key: str):
        del self._metadata[key]

    def format_content(self, content: str) -> str:
        format_args = dict(
            channel=self.channel,
            message=self.message,
            reaction=self.reaction,
            author=self.author,
            actor=self.actor,
            member=self.member,
        )
        format_args.update(self._metadata)
        return content.format_map(format_args)
