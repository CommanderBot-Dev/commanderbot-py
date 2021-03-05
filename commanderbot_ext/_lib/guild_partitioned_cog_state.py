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
        for guild_state in self.guild_states.available:
            if self.ack_guild(guild_state.guild):
                yield guild_state

    async def on_connect(self):
        for guild_state in self.guild_states_to_ack:
            await guild_state.on_connect()

    async def on_disconnect(self):
        for guild_state in self.guild_states_to_ack:
            await guild_state.on_disconnect()

    async def on_ready(self):
        for guild_state in self.guild_states_to_ack:
            await guild_state.on_ready()

    async def on_resumed(self):
        for guild_state in self.guild_states_to_ack:
            await guild_state.on_resumed()

    async def on_user_update(self, before: User, after: User):
        for guild_state in self.guild_states_to_ack:
            await guild_state.on_user_update(before, after)

    async def on_typing(self, channel: Messageable, user: MemberOrUser, when: datetime):
        if text_channel := self.ack_channel_to_text_channel(channel):
            guild = self.ack_guild(text_channel.guild)
            member = self.ack_user_to_member(user)
            if guild and member:
                await self.guild_states[guild].on_typing(text_channel, member, when)

    async def on_message(self, message: Message):
        if text_message := self.ack_message_to_text_message(message):
            if guild := self.ack_guild(text_message.guild):
                await self.guild_states[guild].on_message(text_message)

    async def on_message_delete(self, message: Message):
        if text_message := self.ack_message_to_text_message(message):
            if guild := self.ack_guild(text_message.guild):
                await self.guild_states[guild].on_message_delete(text_message)

    async def on_message_edit(self, before: Message, after: Message):
        # There isn't much point in ack'ing the message pre-edit (it was likely to have
        # already been ack'd by a previous handler) so just ack it post-edit.
        if text_message := self.ack_message_to_text_message(after):
            if guild := self.ack_guild(text_message.guild):
                await self.guild_states[guild].on_message(text_message)

    async def on_reaction_add(self, reaction: Reaction, user: MemberOrUser):
        if text_reaction := self.ack_reaction_to_text_reaction(reaction):
            guild = self.ack_guild(text_reaction.message.guild)
            member = self.ack_user_to_member(user)
            if guild and member:
                await self.guild_states[guild].on_reaction_add(text_reaction, member)

    async def on_reaction_remove(self, reaction: Reaction, user: MemberOrUser):
        if text_reaction := self.ack_reaction_to_text_reaction(reaction):
            guild = self.ack_guild(text_reaction.message.guild)
            member = self.ack_user_to_member(user)
            if guild and member:
                await self.guild_states[guild].on_reaction_remove(text_reaction, member)

    async def on_member_join(self, member: Member):
        guild = self.ack_guild(member.guild)
        if guild and self.ack_user(member):
            await self.guild_states[guild].on_member_join(member)

    async def on_member_remove(self, member: Member):
        guild = self.ack_guild(member.guild)
        if guild and self.ack_user(member):
            await self.guild_states[guild].on_member_remove(member)

    async def on_member_update(self, before: Member, after: Member):
        guild = self.ack_guild(after.guild)
        if guild and self.ack_user(after):
            await self.guild_states[guild].on_member_update(before, after)

    async def on_member_ban(self, guild: Guild, user: MemberOrUser):
        member = self.ack_user_to_member(user)
        if guild and member:
            await self.guild_states[guild].on_member_ban(guild, member)

    async def on_member_unban(self, guild: Guild, user: MemberOrUser):
        member = self.ack_user_to_member(user)
        if guild and member:
            await self.guild_states[guild].on_member_unban(guild, member)
