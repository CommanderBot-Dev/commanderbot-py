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

    async def show_invite(self, ctx: Context, invite_query: str):
        if guild_state := await self.get_guild_state(ctx.guild):
            pass