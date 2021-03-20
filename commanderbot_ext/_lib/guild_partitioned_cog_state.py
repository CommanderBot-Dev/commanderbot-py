from dataclasses import dataclass
from datetime import datetime
from typing import Generic, Iterable, TypeVar

from commanderbot_lib.types import MemberOrUser
from discord import Guild, Member, Message, Reaction, User
from discord.abc import Messageable

from commanderbot_ext._lib.cog_guild_state import CogGuildState
from commanderbot_ext._lib.cog_guild_state_manager import CogGuildStateManager
from commanderbot_ext._lib.cog_state import CogState

GuildStateType = TypeVar("GuildStateType", bound=CogGuildState)


@dataclass
class GuildPartitionedCogState(CogState, Generic[GuildStateType]):
    """
    Additionally maintains a separate state for each guild and forwards them events.

    Less of a stub than it's superclass, this class automatically maintains a lazily-
    initialized map of guild states by guild ID. When an event handler is called, this
    class will notify guild states and create new ones as necessary.

    Also comes with a collection of pre-defined, commonly-used handlers that filter
    guilds, channels, and users. Extend this class with additional handlers if more
    types of events need to be forwarded to guild states.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    guild_states: :class:`CogGuildStateManager`
        A lazily-initialized map of guild states, by guild ID.
    """

    guild_states: CogGuildStateManager[GuildStateType]

    @property
    def guild_states_to_ack(self) -> Iterable[GuildStateType]:
        """ Yield states for ack'd guilds. """
        for guild_state in self.guild_states.available:
            # Make sure the guild should be ack'd.
            if self.ack_guild(guild_state.guild):
                yield guild_state

    async def on_connect(self):
        """ Forward `on_connect` events to existing states of ack'd guilds. """
        for guild_state in self.guild_states_to_ack:
            await guild_state.on_connect()

    async def on_disconnect(self):
        """ Forward `on_disconnect` events to existing states of ack'd guilds. """
        for guild_state in self.guild_states_to_ack:
            await guild_state.on_disconnect()

    async def on_ready(self):
        """ Forward `on_ready` events to existing states of ack'd guilds. """
        for guild_state in self.guild_states_to_ack:
            await guild_state.on_ready()

    async def on_resumed(self):
        """ Forward `on_resumed` events to existing states of ack'd guilds. """
        for guild_state in self.guild_states_to_ack:
            await guild_state.on_resumed()

    async def on_user_update(self, before: User, after: User):
        """ Forward `on_user_update` events to existing states of ack'd guilds. """
        for guild_state in self.guild_states_to_ack:
            await guild_state.on_user_update(before, after)

    async def on_typing(self, channel: Messageable, user: MemberOrUser, when: datetime):
        """ Forward `on_typing` events to states of ack'd guilds. """
        # Make sure this is a [TextChannel] that's ack'd.
        if text_channel := self.ack_channel_to_text_channel(channel):
            # Make sure both the guild and typer are ack'd.
            guild = self.ack_guild(text_channel.guild)
            member = self.ack_user_to_member(user)
            if guild and member:
                # Forward the `on_typing` event to the individual guild state.
                await self.guild_states[guild].on_typing(text_channel, member, when)

    async def on_message(self, message: Message):
        """ Forward `on_message` events to states of ack'd guilds. """
        # Make sure this is a [TextMessage] (a [Message] in a [TextChannel]) that should
        # be acknowledged.
        if text_message := self.ack_message_to_text_message(message):
            # Make sure the guild should be ack'd.
            if guild := self.ack_guild(text_message.guild):
                # Forward the `on_message` event to the individual guild state.
                await self.guild_states[guild].on_message(text_message)

    async def on_message_delete(self, message: Message):
        """ Forward `on_message_delete` events to states of ack'd guilds. """
        # Make sure this is a [TextMessage] (a [Message] in a [TextChannel]) that should
        # be acknowledged.
        if text_message := self.ack_message_to_text_message(message):
            # Make sure the guild should be ack'd.
            if guild := self.ack_guild(text_message.guild):
                # Forward the `on_message_delete` event to the individual guild state.
                await self.guild_states[guild].on_message_delete(text_message)

    async def on_message_edit(self, before: Message, after: Message):
        """ Forward `on_message_edit` events to states of ack'd guilds. """
        # Make sure this is a [TextMessage] (a [Message] in a [TextChannel]) that should
        # be acknowledged. There isn't much point in ack'ing the message pre-edit (it
        # was likely to have already been ack'd by a previous handler) so just ack it
        # post-edit.
        if text_message := self.ack_message_to_text_message(after):
            # Make sure the guild should be ack'd.
            if guild := self.ack_guild(text_message.guild):
                # Forward the `on_message_edit` event to the individual guild state.
                await self.guild_states[guild].on_message(text_message)

    async def on_reaction_add(self, reaction: Reaction, user: MemberOrUser):
        """ Forward `on_reaction_add` events to states of ack'd guilds. """
        # Make sure this is a [TextReaction] (a [Reactiom] on a [TextMessage]) that
        # should be acknowledged.
        if text_reaction := self.ack_reaction_to_text_reaction(reaction):
            # Make sure both the guild and reactor are ack'd.
            guild = self.ack_guild(text_reaction.message.guild)
            member = self.ack_user_to_member(user)
            if guild and member:
                # Forward the `on_reaction_add` event to the individual guild state.
                await self.guild_states[guild].on_reaction_add(text_reaction, member)

    async def on_reaction_remove(self, reaction: Reaction, user: MemberOrUser):
        """ Forward `on_reaction_remove` events to states of ack'd guilds. """
        # Make sure this is a [TextReaction] (a [Reactiom] on a [TextMessage]) that
        # should be acknowledged.
        if text_reaction := self.ack_reaction_to_text_reaction(reaction):
            # Make sure both the guild and reactor are ack'd.
            guild = self.ack_guild(text_reaction.message.guild)
            member = self.ack_user_to_member(user)
            if guild and member:
                # Forward the `on_reaction_remove` event to the individual guild state.
                await self.guild_states[guild].on_reaction_remove(text_reaction, member)

    async def on_member_join(self, member: Member):
        """ Forward `on_member_join` events to states of ack'd guilds. """
        # Make sure the guild should be ack'd, and always ack the user for this event.
        if guild := self.ack_guild(member.guild):
            # Forward the `on_member_join` event to the individual guild state.
            await self.guild_states[guild].on_member_join(member)

    async def on_member_remove(self, member: Member):
        """ Forward `on_member_remove` events to states of ack'd guilds. """
        # Make sure the guild should be ack'd, and always ack the user for this event.
        if guild := self.ack_guild(member.guild):
            # Forward the `on_member_remove` event to the individual guild state.
            await self.guild_states[guild].on_member_remove(member)

    async def on_member_update(self, before: Member, after: Member):
        """ Forward `on_member_update` events to states of ack'd guilds. """
        # Make sure the guild should be ack'd, and always ack the user for this event.
        if guild := self.ack_guild(after.guild):
            # Forward the `on_member_update` event to the individual guild state.
            await self.guild_states[guild].on_member_update(before, after)

    async def on_member_ban(self, guild: Guild, user: MemberOrUser):
        """ Forward `on_member_ban` events to states of ack'd guilds. """
        # Make sure the guild should be ack'd, and always ack the user for this event.
        if self.ack_guild(guild):
            # Forward the `on_member_ban` event to the individual guild state.
            assert isinstance(user, Member)
            await self.guild_states[guild].on_member_ban(guild, user)

    async def on_member_unban(self, guild: Guild, user: MemberOrUser):
        """ Forward `on_member_unban` events to states of ack'd guilds. """
        # Make sure the guild should be ack'd, and always ack the user for this event.
        if self.ack_guild(guild):
            # Forward the `on_member_unban` event to the individual guild state.
            assert isinstance(user, Member)
            await self.guild_states[guild].on_member_unban(guild, user)
