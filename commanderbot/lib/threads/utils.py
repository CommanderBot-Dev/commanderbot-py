from discord import ForumChannel, Thread

__all__ = ("is_pinned", "in_forum_channel")


def is_pinned(thread: Thread) -> bool:
    """
    Returns `True` if the thread is pinned to a forum channel
    """
    return thread.flags.pinned


def in_forum_channel(thread: Thread) -> bool:
    """
    Returns `True` if the thread is in a forum channel
    """
    return isinstance(thread.parent, ForumChannel)
