from dataclasses import dataclass, field
from typing import Tuple

from discord import Thread

from commanderbot.ext.automod.automod_action import AutomodAction, AutomodActionBase
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.lib import JsonObject, RoleID, UserID


@dataclass
class AddUsersToThread(AutomodActionBase):
    """
    Add users to the thread in context.

    Attributes
    ----------
    users
        The users to add to the thread.
    roles
        The roles to add to the thread. Any user with any of these roles will be added.
    """

    users: Tuple[UserID] = field(default_factory=lambda: tuple())
    roles: Tuple[RoleID] = field(default_factory=lambda: tuple())

    async def try_add_user(self, event: AutomodEvent, thread: Thread, user_id: UserID):
        try:
            guild = thread.guild
            assert guild is not None
            member = guild.get_member(user_id)
            assert member is not None
            await thread.add_user(member)
        except:
            event.log.exception(f"Failed to add user {user_id} to thread {thread.id}")

    async def try_add_role(self, event: AutomodEvent, thread: Thread, role_id: RoleID):
        try:
            guild = thread.guild
            assert guild is not None
            role = guild.get_role(role_id)
            assert role is not None
            for member in role.members:
                await thread.add_user(member)
        except:
            event.log.exception(f"Failed to add role {role_id} to thread {thread.id}")

    async def apply(self, event: AutomodEvent):
        if thread := event.thread:
            for user_id in self.users:
                await self.try_add_user(event, thread, user_id)
            for role_id in self.roles:
                await self.try_add_role(event, thread, role_id)


def create_action(data: JsonObject) -> AutomodAction:
    return AddUsersToThread.from_data(data)
