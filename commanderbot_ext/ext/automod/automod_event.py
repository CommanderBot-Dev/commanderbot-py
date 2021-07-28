from dataclasses import dataclass
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


# @implements AutomodEvent
@dataclass
class AutomodEventBase:
    bot: Bot

    def __init__(
        self,
        bot: Bot,
        **data: Dict[str, Any],
    ) -> None:
        self.bot: Bot = bot

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
