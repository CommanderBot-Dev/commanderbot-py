from dataclasses import dataclass

from discord import RawReactionActionEvent

from commanderbot.ext.automod.automod_event import AutomodEventBase

__all__ = ("RawReactionRemoved",)


@dataclass
class RawReactionRemoved(AutomodEventBase):
    payload: RawReactionActionEvent
