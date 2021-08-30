from dataclasses import dataclass

from discord import Member, TextChannel, Thread

from commanderbot.ext.automod.automod_event import AutomodEventBase
from commanderbot.lib.types import TextMessage, TextReaction

__all__ = ("ReactionRemoved",)


@dataclass
class ReactionRemoved(AutomodEventBase):
    _reaction: TextReaction
    _member: Member

    @property
    def channel(self) -> TextChannel | Thread:
        return self._reaction.message.channel

    @property
    def message(self) -> TextMessage:
        return self._reaction.message

    @property
    def reaction(self) -> TextReaction:
        return self._reaction

    @property
    def author(self) -> Member:
        return self._reaction.message.author

    @property
    def actor(self) -> Member:
        return self._member

    @property
    def member(self) -> Member:
        return self._member
