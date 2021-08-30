from dataclasses import dataclass, field
from typing import Iterable, Optional, Set

from discord import Member, Role

from commanderbot_ext.lib.from_data_mixin import FromDataMixin
from commanderbot_ext.lib.types import RoleID
from commanderbot_ext.lib.utils import member_roles_from

__all__ = ("RolesGuard",)


@dataclass
class RolesGuard(FromDataMixin):
    """
    Check whether a member matches a set of roles.

    Attributes
    ----------
    include
        The roles to include. A member will match if they have at least one of these.
    exclude
        The roles to exclude. A member will match if they have none of these.
    """

    include: Set[RoleID] = field(default_factory=set)
    exclude: Set[RoleID] = field(default_factory=set)

    @classmethod
    def try_from_data(cls, data):
        if isinstance(data, dict):
            return cls(
                include=set(data.get("include", [])),
                exclude=set(data.get("exclude", [])),
            )
        elif isinstance(data, list):
            return cls(include=set(data))

    def ignore_by_includes(self, member: Member) -> bool:
        # Ignore roles that are not included, if any.
        if not self.include:
            return False
        matching_roles = member_roles_from(member, self.include)
        return len(matching_roles) == 0

    def ignore_by_excludes(self, member: Member) -> bool:
        # Ignore roles that are excluded, if any.
        if not self.exclude:
            return False
        matching_roles = member_roles_from(member, self.exclude)
        return len(matching_roles) > 0

    def ignore(self, member: Optional[Member]) -> bool:
        """Determine whether to ignore the member based on their roles."""
        if member is None:
            return False
        return self.ignore_by_includes(member) or self.ignore_by_excludes(member)

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
