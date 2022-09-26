from typing import Optional

from discord import ForumChannel, ForumTag

from commanderbot.lib.utils.utils import is_int


def format_tag(tag: ForumTag):
    if tag.emoji:
        return f"{tag.emoji} {tag.name}"
    else:
        return tag.name


def try_get_tag_from_channel(channel: ForumChannel, tag_str: str) -> Optional[ForumTag]:
    """
    Returns a `ForumTag` if it exists in [channel]
    """
    for tag in channel.available_tags:
        if tag.name == tag_str:
            return tag
        elif is_int(tag_str) and tag.id == int(tag_str):
            return tag
