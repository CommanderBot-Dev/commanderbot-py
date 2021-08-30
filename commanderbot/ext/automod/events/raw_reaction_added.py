from dataclasses import dataclass

from discord import RawReactionActionEvent

from commanderbot_ext.ext.automod.automod_event import AutomodEventBase

__all__ = ("RawReactionAdded",)


@dataclass
class RawReactionAdded(AutomodEventBase):
    payload: RawReactionActionEvent
