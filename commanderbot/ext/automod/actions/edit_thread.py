from dataclasses import dataclass
from typing import Optional

from discord import Thread

from commanderbot.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject
from commanderbot.lib.utils import dict_without_nones


@dataclass
class EditThread(AutomodActionBase):
    """
    Edit the thread in context.

    Attributes
    ----------
    name
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

    name: Optional[str] = None
    archived: Optional[bool] = None
    locked: Optional[bool] = None
    slowmode_delay: Optional[int] = None
    auto_archive_duration: Optional[int] = None

    async def apply(self, event: AutomodEvent):
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


def create_action(data: JsonObject) -> AutomodAction:
    return EditThread.from_data(data)
