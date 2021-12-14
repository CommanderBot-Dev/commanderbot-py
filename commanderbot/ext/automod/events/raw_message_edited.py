from dataclasses import dataclass

from discord import RawMessageUpdateEvent

from commanderbot.ext.automod.event import EventBase

__all__ = ("RawMessageEdited",)


@dataclass
class RawMessageEdited(EventBase):
    payload: RawMessageUpdateEvent
