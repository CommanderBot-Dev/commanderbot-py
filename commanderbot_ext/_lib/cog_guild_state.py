from dataclasses import dataclass, field
from datetime import datetime

from commanderbot_lib.logging import Logger, get_logger
from discord import Guild, Member, TextChannel, User
from discord.ext.commands import Bot, Cog

from commanderbot_ext._lib.types import TextMessage, TextReaction


@dataclass
class CogGuildState:
    """
    Maintains state-related data for a particular cog within a particular guild.

    This is an abstraction that afford us two main conveniences:
    1. keeping guild-based logic separate from global logic; and
    2. keeping the state of each guild separate from one another.

    Event handlers are pre-defined and can be added-to by sub-classing this class.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    guild: :class:`Guild`
        The discord.py guild being managed.
    """

    bot: Bot
    cog: Cog
    guild: Guild

    log: Logger = field(init=False)

    def __post_init__(self):
        self.log = get_logger(
            f"{self.cog.qualified_name}@{self.guild}"
            + f" ({self.__class__.__name__}#{id(self)})"
        )

    async def on_connect(self):
        """ Optional override to handle `on_connect` events. """

    async def on_disconnect(self):
        """ Optional override to handle `on_disconnect` events. """

    async def on_ready(self):
        """ Optional override to handle `on_ready` events. """

    async def on_resumed(self):
        """ Optional override to handle `on_resumed` events. """

    async def on_user_update(self, before: User, after: User):
        """ Optional override to handle `on_user_update` events. """

    async def on_typing(self, channel: TextChannel, member: Member, when: datetime):
        """ Optional override to handle `on_typing` events. """

    async def on_message(self, message: TextMessage):
        """ Optional override to handle `on_message` events. """

    async def on_message_delete(self, message: TextMessage):
        """ Optional override to handle `on_message_delete` events. """

    async def on_message_edit(self, before: TextMessage, after: TextMessage):
        """ Optional override to handle `on_message_edit` events. """

    async def on_reaction_add(self, reaction: TextReaction, member: Member):
        """ Optional override to handle `on_reaction_add` events. """

    async def on_reaction_remove(self, reaction: TextReaction, member: Member):
        """ Optional override to handle `on_reaction_remove` events. """

    async def on_member_join(self, member: Member):
        """ Optional override to handle `on_member_join` events. """

    async def on_member_remove(self, member: Member):
        """ Optional override to handle `on_member_remove` events. """

    async def on_member_update(self, before: Member, after: Member):
        """ Optional override to handle `on_member_update` events. """

    async def on_member_ban(self, guild: Guild, member: Member):
        """ Optional override to handle `on_member_ban` events. """

    async def on_member_unban(self, guild: Guild, member: Member):
        """ Optional override to handle `on_member_unban` events. """
