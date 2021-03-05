from datetime import datetime

from commanderbot_lib.types import MemberOrUser
from discord import Guild, Member, Message, Reaction
from discord.abc import Messageable


class Handlers:
    async def on_connect(self):
        """
        Optional override to handle `on_connect` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_connect
        """

    async def on_disconnect(self):
        """
        Optional override to handle `on_disconnect` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_disconnect
        """

    async def on_ready(self):
        """
        Optional override to handle `on_ready` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_ready
        """

    async def on_resumed(self):
        """
        Optional override to handle `on_resumed` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_resumed
        """

    async def on_user_update(self, before: Member, after: Member):
        """
        Optional override to handle `on_user_update` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_user_update
        """

    async def on_typing(self, channel: Messageable, user: MemberOrUser, when: datetime):
        """
        Optional override to handle `on_typing` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_typing
        """

    async def on_message(self, message: Message):
        """
        Optional override to handle `on_message` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_message
        """

    async def on_message_delete(self, message: Message):
        """
        Optional override to handle `on_message_delete` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_message_delete
        """

    async def on_message_edit(self, before: Message, after: Message):
        """
        Optional override to handle `on_message_edit` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_message_edit
        """

    async def on_reaction_add(self, reaction: Reaction, user: MemberOrUser):
        """
        Optional override to handle `on_reaction_add` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_reaction_add
        """

    async def on_reaction_remove(self, reaction: Reaction, user: MemberOrUser):
        """
        Optional override to handle `on_reaction_remove` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_reaction_remove
        """

    async def on_member_join(self, member: Member):
        """
        Optional override to handle `on_member_join` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_member_join
        """

    async def on_member_remove(self, member: Member):
        """
        Optional override to handle `on_member_remove` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_member_remove
        """

    async def on_member_update(self, before: Member, after: Member):
        """
        Optional override to handle `on_member_update` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_member_update
        """

    async def on_member_ban(self, guild: Guild, user: MemberOrUser):
        """
        Optional override to handle `on_member_ban` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_member_ban
        """

    async def on_member_unban(self, guild: Guild, user: MemberOrUser):
        """
        Optional override to handle `on_member_unban` events.
        https://discordpy.readthedocs.io/en/stable/api.html#discord.on_member_unban
        """
