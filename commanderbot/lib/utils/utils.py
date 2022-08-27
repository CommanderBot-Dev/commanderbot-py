import io
import json
import os
import re
import traceback
from datetime import datetime, timezone
from typing import (
    Any,
    AsyncIterable,
    Callable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    TypeVar,
    cast,
)

from discord import AllowedMentions, File, Member, Message, TextChannel, Thread, User
from discord.abc import Messageable
from discord.ext.commands import Bot, Context

from commanderbot.lib.types import RoleID

CHARACTER_CAP = 1900


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


def format_context_cause(ctx: Context) -> str:
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

    return " ".join(parts)


def utcnow_aware() -> datetime:
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def message_to_file(message: Message, filename: Optional[str] = None) -> File:
    filename = filename or "message.md"
    file_lines = []
    if message.content:
        file_lines.append(message.content)
    if message.attachments:
        file_lines += ["", "#### Attachments"]
        for att in message.attachments:
            att_json = json.dumps(att.to_dict(), indent=2)
            file_lines.append(f"\n```json\n{att_json}\n```")
    if message.embeds:
        file_lines += ["", "#### Embeds"]
        for embed in message.embeds:
            embed_json = json.dumps(embed.to_dict(), indent=2)
            file_lines.append(f"\n```json\n{embed_json}\n```")
    file_content = "\n".join(file_lines)
    fp = cast(Any, io.StringIO(file_content))
    file = File(fp=fp, filename=filename)
    return file


def str_to_file(contents: str, filename: str) -> File:
    fp = io.BytesIO(contents.encode())
    return File(fp=fp, filename=filename)


async def send_message_or_file(
    destination: Messageable,
    content: str,
    *,
    file_callback: Callable[[], Tuple[str, str, str]],
    allowed_mentions: AllowedMentions,
    character_cap: int = CHARACTER_CAP,
    **kwargs,
) -> Message:
    """
    Send `content` as a message if it fits, otherwise attach it as a file.

    Arguments
    ---------
    destination
        The destination (channel) to send the message (or upload the file) to.
    content
        The message content to send, if it fits.
    callback
        A callback to determine the alternate message content, file content, and file
        name in case a file needs to be uploaded instead. Note that the alternate
        message content should be guaranteed to fit withint he message cap.
    cap
        The message character cap to check against, if different than the default.
    """
    if len(content) < character_cap:
        return await destination.send(content, allowed_mentions=allowed_mentions)
    else:
        alt_content, file_content, file_name = file_callback()
        fp = cast(Any, io.StringIO(file_content))
        file = File(fp=fp, filename=file_name)
        return await destination.send(
            alt_content,
            file=file,
            allowed_mentions=allowed_mentions,
            **kwargs,
        )
