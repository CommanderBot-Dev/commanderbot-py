from dataclasses import dataclass

from discord import RawReactionActionEvent

from commanderbot_ext.ext.automod.automod_event import AutomodEventBase

__all__ = ("RawReactionRemoved",)


@dataclass
class RawReactionRemoved(AutomodEventBase):
    payload: RawReactionActionEvent
