from dataclasses import dataclass
from typing import Any

from commanderbot.ext.automod.action import Action, ActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent


@dataclass
class JoinThread(ActionBase):
    """
    Join the thread in context.

    Even though bots receive events for a thread, they are not listed as a member of the
    thread automatically. This can cause issues with sending messages; for example, the
    first message may be duplicated if the bot is not listed as a member of it.
    """

    async def apply(self, event: AutomodEvent):
        if thread := event.thread:
            await thread.join()


def create_action(data: Any) -> Action:
    return JoinThread.from_data(data)
