from dataclasses import dataclass
from typing import Any, Iterable, Tuple

from discord import Member

from commanderbot_ext.ext.automod.automod_event import AutomodEventBase
from commanderbot_ext.lib.utils import yield_member_date_fields

__all__ = ("MemberJoined",)


@dataclass
class MemberJoined(AutomodEventBase):
    _member: Member

    @property
    def member(self) -> Member:
        return self._member

    def _yield_extra_fields(self) -> Iterable[Tuple[str, Any]]:
        yield from yield_member_date_fields(self.member)
