from logging import Logger
from typing import Any, Dict, Optional, Protocol

from discord import Member, TextChannel, Thread, User
from discord.ext.commands import Bot

from commanderbot.ext.automod.event.event_state import EventState
from commanderbot.lib import TextMessage, TextReaction

__all__ = ("Event",)


class Event(Protocol):
    state: EventState
    bot: Bot
    log: Logger

    @property
    def channel(self) -> Optional[TextChannel | Thread]:
        """Return the relevant channel, if any."""

    @property
    def thread(self) -> Optional[Thread]:
        """Return the relevant thread, if any."""

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

    def get_fields(self, unsafe: bool = False) -> Dict[str, Any]:
        """Get the full event data."""

    def format_content(self, content: str, *, unsafe: bool = False) -> str:
        """Format a string with event data."""
