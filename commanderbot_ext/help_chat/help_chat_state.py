from datetime import datetime
from typing import List, Union

from commanderbot_ext.help_chat.help_chat_guild_state import HelpChatGuildState
from commanderbot_ext.help_chat.help_chat_options import HelpChatOptions
from commanderbot_ext.help_chat.help_chat_store import HelpChatStore
from commanderbot_lib.state.abc.cog_state import CogState
from discord import CategoryChannel, TextChannel
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

    async def add_channels(self, ctx: Context, channels: List[Union[TextChannel, CategoryChannel]]):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.add_channels(ctx, channels)

    async def remove_channels(
        self, ctx: Context, channels: List[Union[TextChannel, CategoryChannel]]
    ):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.remove_channels(ctx, channels)

    async def set_default_report_split_length(self, ctx: Context, split_length: int):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.set_default_report_split_length(ctx, split_length)

    async def set_default_report_max_rows(self, ctx: Context, max_rows: int):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.set_default_report_max_rows(ctx, max_rows)

    async def set_default_report_min_score(self, ctx: Context, min_score: int):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.set_default_report_min_score(ctx, min_score)

    async def build_report(self, ctx: Context, after: datetime, before: datetime, title: str):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.build_report(ctx, after, before, title)
