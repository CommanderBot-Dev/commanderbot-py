from dataclasses import dataclass, field
from typing import Iterable, Set, Type, TypeVar

from discord import Member, Role

from commanderbot_ext.ext.automod.automod_event import AutomodEvent
from commanderbot_ext.lib import JsonObject, RoleID
from commanderbot_ext.lib.utils import member_roles_from

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

    def ignore_by_includes(self, member: Member) -> bool:
        # If `includes` roles are configured, ignore any events not sent by a member.
        member_roles = member_roles_from(member, self.include)
        return bool(self.include) and not member_roles

    def ignore_by_excludes(self, member: Member) -> bool:
        # If `exclude` roles are configured, ignore any event sent by a member.
        member_roles = member_roles_from(member, self.exclude)
        return bool(self.exclude) and bool(member_roles)

    def ignore(self, event: AutomodEvent) -> bool:
        """Determine whether to ignore the event based on the guard."""
        if author := event.author:
            return self.ignore_by_includes(author) or self.ignore_by_excludes(author)
        return True

    def matches(self, role: Role) -> bool:
        """Check whether a role matches the guard."""
        # Note that `include` takes precedence over `exclude`.
        if self.include:
            return role.id in self.include
        if self.exclude:
            return role.id not in self.exclude
        return True

    def filter(self, roles: Iterable[Role]) -> Set[Role]:
        """Filter a set of roles based on the guard."""
        return {role for role in roles if self.matches(role)}
