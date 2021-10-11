from dataclasses import dataclass

from discord import RawReactionActionEvent

from commanderbot.ext.automod.event import EventBase

__all__ = ("RawReactionRemoved",)


@dataclass
class RawReactionRemoved(EventBase):
    payload: RawReactionActionEvent
