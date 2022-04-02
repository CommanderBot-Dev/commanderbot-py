import difflib
import re
from typing import List, Tuple

from discord import Role
from discord.ext.commands import BadArgument, RoleConverter, RoleNotFound

from commanderbot.lib.types import GuildContext

__all__ = (
    "CannotDisambiguateRole",
    "LenientRoleConverter",
)


class CannotDisambiguateRole(BadArgument):
    """Exception raised when multiple roles match the argument."""

    def __init__(self, argument: str, roles: List[Role]):
        self.argument: str = argument
        count_roles = len(roles)
        role_mentions = " ".join(f"{role.mention}" for role in roles)
        super().__init__(
            f"Cannot disambiguate role `{argument}` with {count_roles} matches: "
            + role_mentions
        )


class LenientRoleConverter(RoleConverter):
    """
    Extends `RoleConverter` to do one final look-up using a partial name match.

    Raises `CannotDisambiguateRole` if multiple roles are matched.
    """

    async def convert(self, ctx: GuildContext, argument: str) -> Role:
        # Attempt to look-up the role as usual.
        try:
            if role := await super().convert(ctx, argument):
                if role.id != ctx.guild.default_role.id:
                    raise RoleNotFound(argument)
                return role
        except RoleNotFound:
            pass

        # If nothing was found, use a more lenient approach...

        # Use regex to do a partial match, with the input escaped.
        escaped = re.escape(argument)
        pattern = re.compile(f"\\b{escaped}\\b", re.IGNORECASE)
        matches = self.filter_roles(ctx, argument, pattern)

        # If exactly one role was found, return it.
        if len(matches) == 1:
            return matches[0]

        # If multiple roles were found, use difflib to grab the best match.
        if len(matches) > 1:
            rated_matches = self.rate_matches(argument, matches)
            first_place = rated_matches[0]
            second_place = rated_matches[1]

            # If there's exactly 1 best match, return it.
            if first_place[0] > second_place[0]:
                return first_place[1]

            # Otherwise, we cannot disambiguate.
            raise CannotDisambiguateRole(argument, matches)

        # If still nothing was found, raise.
        raise RoleNotFound(argument)

    def filter_roles(
        self, ctx: GuildContext, argument: str, pattern: re.Pattern
    ) -> List[Role]:
        roles = list(ctx.guild.roles)
        roles.remove(ctx.guild.default_role)
        return [role for role in roles if self.match_role(ctx, argument, pattern, role)]

    def match_role(
        self, ctx: GuildContext, argument: str, pattern: re.Pattern, role: Role
    ) -> bool:
        match = pattern.search(role.name)
        return match is not None

    def rate_matches(
        self, argument: str, matches: List[Role]
    ) -> List[Tuple[float, Role]]:
        return sorted(
            [
                (difflib.SequenceMatcher(None, argument, role.name).ratio(), role)
                for role in matches
            ],
            reverse=True,
        )
