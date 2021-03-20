from commanderbot_lib.state.abc.cog_state import CogState
from discord import Message
from discord.ext.commands import Context

from commanderbot_ext.invite.invite_guild_state import InviteGuildState
from commanderbot_ext.invite.invite_options import InviteOptions
from commanderbot_ext.invite.invite_store import InviteStore


class InviteState(CogState[InviteOptions, InviteStore, InviteGuildState]):
    store_class = InviteStore
    guild_state_class = InviteGuildState

    async def list_invites(self, ctx: Context):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.list_invites(ctx)

    async def show_invite(self, ctx: Context, invite: str):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.show_invite(ctx, invite)

    async def add_invite(self, ctx: Context, link: str):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.add_invite(ctx, link)

    async def update_invite(self, ctx: Context, name: str, link: str):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.update_invite(ctx, name, link)

    async def remove_invite(self, ctx: Context, name: str):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.remove_invite(ctx, name)

    async def details(self, ctx: Context, name: str):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.details(ctx, name)

    async def add_tag(self, ctx: Context, name: str, tag: str):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.add_tag(ctx, name, tag)

    async def remove_tag(self, ctx: Context, name: str, tag: str):
        if guild_state := await self.get_guild_state(ctx.guild):
            await guild_state.remove_tag(ctx, name, tag)
