from dataclasses import dataclass

from discord import Member

from commanderbot_ext.ext.automod.automod_event import AutomodEventBase

__all__ = ("MemberJoined",)


@dataclass
class MemberJoined(AutomodEventBase):
    _member: Member

    @property
    def member(self) -> Member:
        return self._member
