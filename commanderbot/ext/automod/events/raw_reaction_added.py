from dataclasses import dataclass

from discord import RawReactionActionEvent

from commanderbot.ext.automod.event import EventBase

__all__ = ("RawReactionAdded",)


@dataclass
class RawReactionAdded(EventBase):
    payload: RawReactionActionEvent
