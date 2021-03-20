from datetime import datetime

from commanderbot_lib.guild_state.abc.cog_guild_state import CogGuildState
from discord import Message
from discord.ext.commands import Context

from commanderbot_ext.invite.invite_cache import InviteEntry
from commanderbot_ext.invite.invite_options import InviteOptions
from commanderbot_ext.invite.invite_store import InviteStore


class InviteGuildState(CogGuildState[InviteOptions, InviteStore]):
    async def list_invites(self, ctx: Context):
        if entries := await self.store.iter_guild_invites(self.guild):
            # Sort entries by hits -> name.
            sorted_entries = sorted(entries, key=lambda entry: (entry.hits, entry.name))
            count = len(sorted_entries)
            invite_names = (entry.name for entry in sorted_entries)
            text = f"There are {count} invites available: `" + "` `".join(invite_names) + "`"
            await ctx.send(text)
        else:
            await ctx.send(f"No invites available")