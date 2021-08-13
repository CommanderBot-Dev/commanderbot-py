from typing import Any, AsyncIterable, List, Mapping, Optional, Set, Type, TypeVar

from commanderbot import CommanderBotBase
from discord import Color, Member
from discord.ext.commands import Bot, Cog, ColourConverter

from commanderbot_ext.lib.types import RoleID

DEFAULT: Any = object()


T = TypeVar("T")


def check_commander_bot(bot: Bot) -> Optional[CommanderBotBase]:
    if isinstance(bot, CommanderBotBase):
        return bot


def add_configured_cog(bot: Bot, ext_name: str, cog_class: Type[Cog]):
    cog = None
    if cb := check_commander_bot(bot):
        if options := cb.get_extension_options(ext_name):
            cog = cog_class(bot, **options)
    if not cog:
        cog = cog_class(bot)
    bot.add_cog(cog)


def is_bot(bot: Bot, user: Any) -> bool:
    return user == bot.user or getattr(user, "bot")


def member_roles_from(member: Member, role_ids: Set[RoleID]) -> Set[RoleID]:
    """Return the set of matching member roles."""
    member_role_ids = {role.id for role in member.roles}
    matching_role_ids = role_ids.intersection(member_role_ids)
    return matching_role_ids


def color_from_hex(hex: str) -> Color:
    if hex.startswith("#"):
        arg = hex[1:]
    else:
        arg = hex
    return ColourConverter().parse_hex_number(arg)


def color_to_hex(color: Color) -> str:
    return str(color)


def dict_without_nones(d: Optional[Mapping[str, Any]] = None, **kwargs):
    dd = dict(d, **kwargs) if d else kwargs
    return {k: v for k, v in dd.items() if v is not None}


def dict_without_ellipsis(d: Optional[Mapping[str, Any]] = None, **kwargs):
    dd = dict(d, **kwargs) if d else kwargs
    return {k: v for k, v in dd.items() if v is not ...}


def dict_without_falsies(d: Optional[Mapping[str, Any]] = None, **kwargs):
    dd = dict(d, **kwargs) if d else kwargs
    return {k: v for k, v in dd.items() if v}


async def async_expand(it: AsyncIterable[T]) -> List[T]:
    return [value async for value in it]
