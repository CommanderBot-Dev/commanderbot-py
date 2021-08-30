from dataclasses import dataclass

from discord import Member

from commanderbot_ext.ext.automod.automod_event import AutomodEventBase

__all__ = ("MemberUpdated",)


@dataclass
class MemberUpdated(AutomodEventBase):
    _before: Member
    _after: Member

    @property
    def actor(self) -> Member:
        return self._after

    @property
    def member(self) -> Member:
        return self._after
