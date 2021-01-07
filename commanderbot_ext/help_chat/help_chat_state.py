from datetime import datetime
from typing import List

from commanderbot_ext.help_chat.help_chat_guild_state import HelpChatGuildState
from commanderbot_ext.help_chat.help_chat_options import HelpChatOptions
from commanderbot_ext.help_chat.help_chat_store import HelpChatStore
from commanderbot_lib.state.abc.cog_state import CogState
from discord import TextChannel
from discord.ext.commands import Context


class HelpChatState(CogState[HelpChatOptions, HelpChatStore, HelpChatGuildState]):
    store_class = HelpChatStore
    guild_state_class = HelpChatGuildState

    async def show_channels(self, ctx: Context):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.show_channels(ctx)

    async def list_channels(self, ctx: Context):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.list_channels(ctx)

    async def add_channels(self, ctx: Context, channels: List[TextChannel]):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.add_channels(ctx, channels)

    async def remove_channels(self, ctx: Context, channels: List[TextChannel]):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.remove_channels(ctx, channels)

    async def build_nominations(self, ctx: Context, after: datetime, before: datetime):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.build_nominations(ctx, after, before)
