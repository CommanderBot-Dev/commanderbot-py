from typing import List, Optional

from discord import ForumChannel, ForumTag, Thread

from commanderbot.lib.types import ForumTagID
from commanderbot.lib.utils.utils import is_int

__all__ = (
    "format_tag",
    "try_get_tag",
    "try_get_tag_insensitive",
    "tags_from_ids",
    "tag_from_id",
    "has_tag",
)


def format_tag(tag: ForumTag):
    if tag.emoji:
        return f"{tag.emoji} {tag.name}"
    else:
        return tag.name


def try_get_tag(channel: ForumChannel, tag_str: str) -> Optional[ForumTag]:
    """
    Returns a `ForumTag` if it exists in [channel]
    """
    for tag in channel.available_tags:
        if tag.name == tag_str:
            return tag
        elif is_int(tag_str) and tag.id == int(tag_str):
            return tag


def try_get_tag_insensitive(channel: ForumChannel, tag_str: str) -> Optional[ForumTag]:
    """
    Returns a `ForumTag` if it exists in [channel]

    `tag_str` is compared in a case insensitive way
    """
    for tag in channel.available_tags:
        if tag.name.lower() == tag_str.lower():
            return tag
        elif is_int(tag_str) and tag.id == int(tag_str):
            return tag


def tags_from_ids(channel: ForumChannel, *ids: ForumTagID) -> List[ForumTag]:
    return [i for i in channel.available_tags if i in ids]


def tag_from_id(channel: ForumChannel, id: ForumTagID) -> Optional[ForumTag]:
    for tag in channel.available_tags:
        if tag.id == id:
            return tag


def has_tag(channel: ForumChannel, id: ForumTagID) -> bool:
    for tag in channel.available_tags:
        if tag.id == id:
            return True
    return False


def is_pinned(thread: Thread) -> bool:
    """
    Returns `True` if the thread is pinned to the forum channel
    """
    return thread.flags.pinned


def in_forum_channel(thread: Thread) -> bool:
    """
    Returns `True` if the thread is in a forum channel
    """
    return isinstance(thread.parent, ForumChannel)
