from dataclasses import dataclass
from typing import Any, Optional

from discord import Thread

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.event import Event
from commanderbot.lib.utils import dict_without_nones


@dataclass
class EditThread(ActionBase):
    """
    Edit the thread in context.

    Attributes
    ----------
    thread_name
        The new name of the thread.
    archived
        Whether to archive the thread or not.
    locked
        Whether to lock the thread or not.
    slowmode_delay
        Specifies the slowmode rate limit for user in this thread, in seconds.
        A value of ``0`` disables slowmode. The maximum value possible is ``21600``.
    auto_archive_duration
        The new duration in minutes before a thread is automatically archived for
        inactivity. Must be one of ``60``, ``1440``, ``4320``, or ``10080``.
    """

    thread_name: Optional[str] = None
    archived: Optional[bool] = None
    locked: Optional[bool] = None
    slowmode_delay: Optional[int] = None
    auto_archive_duration: Optional[int] = None

    async def apply(self, event: Event):
        thread = event.channel
        if not isinstance(thread, Thread):
            return
        params = dict_without_nones(
            name=self.name,
            archived=self.archived,
            locked=self.locked,
            slowmode_delay=self.slowmode_delay,
            auto_archive_duration=self.auto_archive_duration,
        )
        await thread.edit(**params)


def create_action(data: Any) -> Action:
    return EditThread.from_data(data)
