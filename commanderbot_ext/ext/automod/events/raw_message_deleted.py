from dataclasses import dataclass

from discord import RawMessageDeleteEvent

from commanderbot_ext.ext.automod.automod_event import AutomodEventBase

__all__ = ("RawMessageDeleted",)


@dataclass
class RawMessageDeleted(AutomodEventBase):
    payload: RawMessageDeleteEvent
