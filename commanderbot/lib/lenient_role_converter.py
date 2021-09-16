import re
from typing import List

from discord import Role
from discord.ext.commands import BadArgument, RoleConverter, RoleNotFound

from commanderbot.lib.types import GuildContext

__all__ = (
    "CannotDisambiguateRole",
    "LenientRoleConverter",
    "LenientRole",
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
        # Use regex to do a partial match, with the input escaped.
        escaped = re.escape(argument)
        pattern = re.compile(f"\\b{escaped}\\b", re.IGNORECASE)

        # Attempt to look-up the role as usual.
        try:
            if role := await super().convert(ctx, argument):
                if role.id != ctx.guild.default_role.id:
                    raise RoleNotFound(argument)
                return role
        except RoleNotFound:
            pass

        # If nothing was found, proceed to use a more lenient approach.
        roles = self.filter_roles(ctx, argument, pattern)

        # If exactly one role was found, return it.
        if len(roles) == 1:
            return roles[0]

        # If multiple roles were found, raise.
        if len(roles) > 1:
            raise CannotDisambiguateRole(argument, roles)

        # If still nothing was found, raise.
        raise RoleNotFound(argument)

    def filter_roles(
        self, ctx: GuildContext, argument: str, pattern: re.Pattern
    ) -> List[Role]:
        roles = ctx.guild.roles
        roles.remove(ctx.guild.default_role)
        return [role for role in roles if self.match_role(ctx, argument, pattern, role)]

    def match_role(
        self, ctx: GuildContext, argument: str, pattern: re.Pattern, role: Role
    ) -> bool:
        match = pattern.search(role.name)
        return match is not None


class LenientRole(LenientRoleConverter, Role):
    pass
