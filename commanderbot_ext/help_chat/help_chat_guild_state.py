from datetime import datetime
from typing import List

from commanderbot_ext.help_chat.help_chat_cache import HelpChannel
from commanderbot_ext.help_chat.help_chat_nom_context import HelpChatNomContext
from commanderbot_ext.help_chat.help_chat_options import HelpChatOptions
from commanderbot_ext.help_chat.help_chat_store import HelpChatStore
from commanderbot_lib.guild_state.abc.cog_guild_state import CogGuildState
from discord import TextChannel
from discord.ext.commands import Context


class HelpChatGuildState(CogGuildState[HelpChatOptions, HelpChatStore]):
    async def show_channels(self, ctx: Context):
        if help_channels := self.store.iter_guild_help_channels(self.guild):
            channels = [help_channel.channel(ctx) for help_channel in help_channels]
            sorted_channels = sorted(channels, key=lambda channel: channel.position)
            await ctx.send(
                f"There are {len(sorted_channels)} help channels registered: "
                + " ".join(ch.mention for ch in sorted_channels)
            )
        else:
            await ctx.send(f"No help channels registered")

    async def list_channels(self, ctx: Context):
        if help_channels := self.store.iter_guild_help_channels(self.guild):
            lines = []
            for help_channel in help_channels:
                channel = help_channel.channel(ctx)
                lines.append(f"{channel.mention} registered on {help_channel.registered_on}")
            await ctx.send(
                f"There are {len(help_channels)} help channels registered:\n" + "\n".join(lines)
            )
        else:
            await ctx.send(f"No help channels registered")

    async def add_channels(self, ctx: Context, channels: List[TextChannel]):
        added_help_channels: List[TextChannel] = []
        already_help_channels: List[TextChannel] = []
        failed_channels: List[TextChannel] = []

        now = datetime.utcnow()

        for channel in channels:
            try:
                if help_channel := await self.store.get_guild_help_channel(self.guild, channel):
                    already_help_channels.append(channel)
                else:
                    help_channel = HelpChannel(
                        channel_id=channel.id,
                        registered_on=now,
                    )
                    await self.store.add_guild_help_channel(self.guild, help_channel)
                    added_help_channels.append(channel)
            except:
                self._log.exception("Failed to register help channel")
                failed_channels.append(channel)

        if added_help_channels:
            await ctx.send(
                f"✅ These {len(added_help_channels)} channels are now help channels: "
                + " ".join(ch.mention for ch in added_help_channels)
            )

        if already_help_channels:
            await ctx.send(
                f"💡 These {len(already_help_channels)} channels were already help channels and "
                + "haven't changed: "
                + " ".join(ch.mention for ch in already_help_channels)
            )

        if failed_channels:
            await ctx.send(
                f"⚠️ These {len(failed_channels)} channels caused errors:"
                + " ".join(ch.mention for ch in failed_channels)
            )

    async def remove_channels(self, ctx: Context, channels: List[TextChannel]):
        removed_help_channels: List[TextChannel] = []
        not_help_channels: List[TextChannel] = []
        failed_channels: List[TextChannel] = []

        for channel in channels:
            try:
                if help_channel := await self.store.get_guild_help_channel(self.guild, channel):
                    await self.store.remove_guild_help_channel(self.guild, help_channel)
                    removed_help_channels.append(channel)
                else:
                    not_help_channels.append(channel)
            except:
                self._log.exception("Failed to deregister help channel")
                failed_channels.append(channel)

        if removed_help_channels:
            await ctx.send(
                f"✅ These {len(removed_help_channels)} channels are **no longer** help channels: "
                + " ".join(ch.mention for ch in removed_help_channels)
            )

        if not_help_channels:
            await ctx.send(
                f"💡 These {len(not_help_channels)} channels were **not** already help channels "
                + "and haven't changed: "
                + " ".join(ch.mention for ch in not_help_channels)
            )

        if failed_channels:
            await ctx.send(
                f"⚠️ These {len(failed_channels)} channels caused errors:"
                + " ".join(ch.mention for ch in failed_channels)
            )

    async def build_nominations(self, ctx: Context, after: datetime, before: datetime):
        help_channels: List[HelpChannel] = list(self.store.iter_guild_help_channels(self.guild))
        nom_context = HelpChatNomContext(
            ctx, options=self.options, help_channels=help_channels, after=after, before=before
        )
        await nom_context.run()
