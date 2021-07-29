from dataclasses import dataclass, field
from typing import Set, Type, TypeVar

from discord import Member

from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject, RoleID
from commanderbot_ext.lib.utils import dict_without_ellipsis, member_roles_from

ST = TypeVar("ST")


@dataclass
class AutomodRolesGuard:
    include: Set[RoleID] = field(default_factory=set)
    exclude: Set[RoleID] = field(default_factory=set)

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        return cls(
            include=set(data.get("include", [])),
            exclude=set(data.get("exclude", [])),
        )

    def to_data(self) -> JsonObject:
        return dict_without_ellipsis(
            include=list(self.include) or ...,
            exclude=list(self.exclude) or ...,
        )

    def ignore_by_includes(self, member: Member) -> bool:
        # If `includes` roles are configured, ignore any events not sent by a member.
        member_roles = member_roles_from(member, self.include)
        return bool(self.include) and not member_roles

    def ignore_by_excludes(self, member: Member) -> bool:
        # If `exclude` roles are configured, ignore any event sent by a member.
        member_roles = member_roles_from(member, self.exclude)
        return bool(self.exclude) and bool(member_roles)

    def ignore(self, event: AutomodEvent) -> bool:
        if author := event.author:
            return self.ignore_by_includes(author) or self.ignore_by_excludes(author)
        return True
