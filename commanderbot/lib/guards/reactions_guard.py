from dataclasses import dataclass, field
from typing import Optional, Set

from discord import Reaction

from commanderbot_ext.lib.from_data_mixin import FromDataMixin
from commanderbot_ext.lib.integer_range import IntegerRange

__all__ = ("ReactionsGuard",)


@dataclass
class ReactionsGuard(FromDataMixin):
    """
    Check whether a reaction matches a set of reactions.

    Attributes
    ----------
    include
        The reactions to include. A reaction will match if it is in this set.
    exclude
        The reactions to exclude. A reaction will match if it is not in this set.
    count
        The number of reactions to check for.
    """

    include: Set[str] = field(default_factory=set)
    exclude: Set[str] = field(default_factory=set)

    count: Optional[IntegerRange] = None

    @classmethod
    def try_from_data(cls, data):
        if isinstance(data, dict):
            return cls(
                include=set(data.get("include", [])),
                exclude=set(data.get("exclude", [])),
                count=IntegerRange.from_field_optional(data, "count"),
            )
        elif isinstance(data, list):
            return cls(include=set(data))

    def ignore_by_includes(self, reaction: Reaction) -> bool:
        # Ignore reactions with emoji that are not included, if any.
        if not self.include:
            return False
        return str(reaction.emoji) not in self.include

    def ignore_by_excludes(self, reaction: Reaction) -> bool:
        # Ignore reactions with emoji that are excluded, if any.
        if not self.exclude:
            return False
        return (self.exclude is not None) and (str(reaction.emoji) in self.exclude)

    def ignore_by_count(self, reaction: Reaction) -> bool:
        # Ignore reactions with a count that is not within the defined range, if any.
        if self.count is None:
            return False
        return self.count.excludes(reaction.count)

    def ignore(self, reaction: Optional[Reaction]) -> bool:
        """Determine whether to ignore the reaction based on the emoji and count."""
        if reaction is None:
            return False
        return (
            self.ignore_by_includes(reaction)
            or self.ignore_by_excludes(reaction)
            or self.ignore_by_count(reaction)
        )
