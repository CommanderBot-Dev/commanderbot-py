from typing import List, Optional

from discord import ForumChannel, ForumTag, Thread

from commanderbot.lib.types import ForumTagID
from commanderbot.lib.utils.utils import is_int

__all__ = (
    "format_tag",
    "try_get_tag",
    "tags_from_ids",
    "has_tag",
)


def format_tag(tag: ForumTag):
    if tag.emoji:
        return f"{tag.emoji} {tag.name}"
    else:
        return tag.name


def try_get_tag(
    channel: ForumChannel, tag_str: str, *, insensitive=False
) -> Optional[ForumTag]:
    """
    Returns a `ForumTag` if it exists in [channel]
    """
    for tag in channel.available_tags:
        if tag.name.lower() == tag_str.lower() if insensitive else tag.name == tag_str:
            return tag
        elif is_int(tag_str) and tag.id == int(tag_str):
            return tag


def tags_from_ids(channel: ForumChannel, *ids: ForumTagID) -> List[ForumTag]:
    return [i for i in channel.available_tags if i in ids]


def has_tag(channel: ForumChannel, id: ForumTagID) -> bool:
    return bool(channel.get_tag(id))
