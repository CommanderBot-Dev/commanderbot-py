from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator, Optional, Set, Tuple, Union

from discord import Guild, Member, Role

from commanderbot.lib.from_data_mixin import FromDataMixin
from commanderbot.lib.json_serializable import JsonSerializable
from commanderbot.lib.types import RoleID

__all__ = ("RoleSet",)


@dataclass(frozen=True)
class RoleSet(JsonSerializable, FromDataMixin):
    """
    Wrapper around a set of role IDs, useful for common set-based operations.

    Attributes
    ----------
    values
        The underlying set of role IDs.
    """

    _values: Set[RoleID] = field(default_factory=set)

    @classmethod
    def try_from_data(cls, data):
        if isinstance(data, dict):
            return cls(
                _values=set(data.get("values", [])),
            )
        elif isinstance(data, list):
            return cls(_values=set(data))

    def __iter__(self) -> Iterator[RoleID]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    # @implements JsonSerializable
    def to_json(self) -> Any:
        return list(self._values)

    def _get_role_id(self, role: Union[Role, RoleID]) -> RoleID:
        if isinstance(role, int):
            return role
        return role.id

    def _get_member_role_ids(self, member: Member) -> Set[RoleID]:
        return {role.id for role in member.roles}

    def iter_roles(self, guild: Guild) -> Iterable[Tuple[RoleID, Optional[Role]]]:
        for role_id in self._values:
            role = guild.get_role(role_id)
            yield role_id, role

    def to_names(self, guild: Guild) -> str:
        return " ".join(
            f"{role.name}" if role else f"`{role_id} (Unknown)`"
            for role_id, role in self.iter_roles(guild)
        )

    def to_mentions(self, guild: Guild) -> str:
        return " ".join(
            f"{role.mention}" if role else f"`{role_id} (Unknown)`"
            for role_id, role in self.iter_roles(guild)
        )

    def add(self, role: Union[Role, RoleID]):
        role_id = self._get_role_id(role)
        self._values.add(role_id)

    def remove(self, role: Union[Role, RoleID]):
        role_id = self._get_role_id(role)
        self._values.remove(role_id)

    def member_has_some(self, member: Member, count: int = 1) -> bool:
        member_role_ids = self._get_member_role_ids(member)
        matching_role_ids = self._values.intersection(member_role_ids)
        has_some = len(matching_role_ids) >= count
        return has_some

    def member_has_all(self, member: Member) -> bool:
        member_role_ids = self._get_member_role_ids(member)
        has_all = member_role_ids >= self._values
        return has_all
