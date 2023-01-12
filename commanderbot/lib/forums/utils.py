from typing import Optional

from discord import ForumChannel, ForumTag

from commanderbot.lib.types import ForumTagID
from commanderbot.lib.utils.utils import is_int

__all__ = (
    "format_tag",
    "try_get_tag",
    "require_tag",
)


def format_tag(tag: ForumTag) -> str:
    if tag.emoji:
        return f"{tag.emoji} {tag.name}"
    else:
        return tag.name


def try_get_tag(
    channel: ForumChannel, tag_str: str, *, case_sensitive=True
) -> Optional[ForumTag]:
    """
    Returns a `ForumTag` if it exists in [channel]
    """
    for tag in channel.available_tags:
        if case_sensitive and tag.name == tag_str:
            return tag
        elif tag.name.lower() == tag_str.lower():
            return tag
        elif is_int(tag_str) and tag.id == int(tag_str):
            return tag


def require_tag(channel: ForumChannel, id: ForumTagID) -> ForumTag:
    if tag := channel.get_tag(id):
        return tag
    raise KeyError(f"<#{channel}> does not have a tag with the ID `{id}`")
