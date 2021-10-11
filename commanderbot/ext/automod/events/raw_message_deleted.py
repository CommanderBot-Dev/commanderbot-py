from dataclasses import dataclass

from discord import RawMessageDeleteEvent

from commanderbot.ext.automod.event import EventBase

__all__ = ("RawMessageDeleted",)


@dataclass
class RawMessageDeleted(EventBase):
    payload: RawMessageDeleteEvent
