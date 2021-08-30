from dataclasses import dataclass

from discord import RawMessageUpdateEvent

from commanderbot.ext.automod.automod_event import AutomodEventBase

__all__ = ("RawMessageEdited",)


@dataclass
class RawMessageEdited(AutomodEventBase):
    payload: RawMessageUpdateEvent
