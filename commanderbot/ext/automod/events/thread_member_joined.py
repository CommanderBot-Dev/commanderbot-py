from dataclasses import dataclass

from discord import Member, Thread, ThreadMember

from commanderbot.ext.automod.event import EventBase

__all__ = ("ThreadMemberJoined",)


@dataclass
class ThreadMemberJoined(EventBase):
    _member: ThreadMember

    @property
    def channel(self) -> Thread:
        return self.thread

    @property
    def thread(self) -> Thread:
        return self._member.thread

    @property
    def member(self) -> Member:
        # ... Seriously?
        member = self._member.thread.guild.get_member(self._member.id)
        assert member is not None
        return member
