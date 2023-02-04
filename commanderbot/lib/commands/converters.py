import difflib
import re
from typing import List, Tuple

import discord
from discord.ext import commands
from discord.ext.commands import Context

from commanderbot.lib import Color, GuildContext

__all__ = (
    "CannotDisambiguateRole",
    "LenientRoleConverter",
    "ColorConverter",
)


class CannotDisambiguateRole(commands.BadArgument):
    """Exception raised when multiple roles match the argument."""

    def __init__(self, argument: str, roles: List[discord.Role]):
        self.argument: str = argument
        count_roles = len(roles)
        role_mentions = " ".join(f"{role.mention}" for role in roles)
        super().__init__(
            f"Cannot disambiguate role `{argument}` with {count_roles} matches: "
            + role_mentions
        )


class LenientRoleConverter(commands.RoleConverter):
    """
    Extends `RoleConverter` to do one final look-up using a partial name match.

    Raises `CannotDisambiguateRole` if multiple roles are matched.
    """

    async def convert(self, ctx: GuildContext, argument: str) -> discord.Role:
        # Attempt to look-up the role as usual.
        try:
            if role := await super().convert(ctx, argument):
                if role.id != ctx.guild.default_role.id:
                    raise commands.RoleNotFound(argument)
                return role
        except commands.RoleNotFound:
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
        raise commands.RoleNotFound(argument)

    def filter_roles(
        self, ctx: GuildContext, argument: str, pattern: re.Pattern
    ) -> List[discord.Role]:
        roles = list(ctx.guild.roles)
        roles.remove(ctx.guild.default_role)
        return [role for role in roles if self.match_role(ctx, argument, pattern, role)]

    def match_role(
        self, ctx: GuildContext, argument: str, pattern: re.Pattern, role: discord.Role
    ) -> bool:
        match = pattern.search(role.name)
        return match is not None

    def rate_matches(
        self, argument: str, matches: List[discord.Role]
    ) -> List[Tuple[float, discord.Role]]:
        return sorted(
            [
                (difflib.SequenceMatcher(None, argument, role.name).ratio(), role)
                for role in matches
            ],
            reverse=True,
        )


class ColorConverter(commands.ColorConverter):
    """Extends `commands.ColorConverter`."""

    # @overrides commands.ColorConverter
    async def convert(self, ctx: Context, argument: str) -> Color:
        temp: discord.Color = await super().convert(ctx, argument)
        return Color(temp.value)
