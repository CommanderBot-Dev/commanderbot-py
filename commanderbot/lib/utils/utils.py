import os
import re
import traceback
from typing import Any, AsyncIterable, List, Mapping, Optional, Set, TypeVar

from discord import Member, TextChannel, Thread, User
from discord.ext.commands import Bot, Context

from commanderbot.lib.types import RoleID

T = TypeVar("T")


def is_bot(bot: Bot, user: Any) -> bool:
    return user == bot.user or getattr(user, "bot")


def member_roles_from(member: User | Member, role_ids: Set[RoleID]) -> Set[RoleID]:
    """
    Return the set of matching member roles.

    A plain [User] may be passed, however an empty set will always be returned.
    """
    if isinstance(member, User):
        return set()
    member_role_ids = {role.id for role in member.roles}
    matching_role_ids = role_ids.intersection(member_role_ids)
    return matching_role_ids


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


def sanitize_stacktrace(error: Exception) -> str:
    lines = traceback.format_exception(
        type(error),
        value=error,
        tb=error.__traceback__,
    )

    def shorten(match):
        abs_path = match.group(1)
        basename = os.path.basename(abs_path)
        return f'File "{basename}"'

    lines = [re.sub(r'File "([^"]+)"', shorten, line, 1) for line in lines]

    return "".join(lines)


def format_command_context(ctx: Context) -> str:
    parts = []

    if author := ctx.author:
        parts.append(author.mention)
    else:
        parts.append("`Unknown User`")

    if channel := ctx.channel:
        if isinstance(channel, TextChannel | Thread):
            parts.append(f"in {channel.mention}")
        else:
            parts.append(f"in channel `{channel}` (ID `{channel.id}`)")
    elif guild := ctx.guild:
        parts.append(f"in guild `{guild}` (ID `{guild.id}`)")

    lines = [
        " ".join(parts) + ":",
        "```",
        str(ctx.command),
        "```",
    ]

    return "\n".join(lines)
