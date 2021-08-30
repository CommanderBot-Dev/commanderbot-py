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
        role_names = " ".join(role.name for role in roles)
        super().__init__(
            f"Cannot disambiguate role `{argument}` with {count_roles} matches: "
            + role_names
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
                return role
        except RoleNotFound:
            pass
        # If nothing was found, proceed to use a more lenient approach.
        roles = self.filter_roles(ctx, argument)
        # If exactly one role was found, return it.
        if len(roles) == 1:
            return roles[0]
        # If multiple roles were found, raise.
        if len(roles) > 1:
            raise CannotDisambiguateRole(argument, roles)
        # If still nothing was found, raise.
        raise RoleNotFound(argument)

    def filter_roles(self, ctx: GuildContext, argument: str) -> List[Role]:
        return [
            role for role in ctx.guild.roles if self.match_role(ctx, argument, role)
        ]

    def match_role(self, ctx: GuildContext, argument: str, role: Role) -> bool:
        return argument in role.name


class LenientRole(LenientRoleConverter, Role):
    pass
