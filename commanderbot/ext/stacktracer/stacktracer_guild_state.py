from dataclasses import dataclass
from typing import Optional

from discord import Color, TextChannel, Thread

from commanderbot.ext.stacktracer.stacktracer_store import StacktracerStore
from commanderbot.lib import AllowedMentions, CogGuildState, GuildContext, LogOptions


@dataclass
class StacktracerGuildState(CogGuildState):
    """
    Encapsulates the state and logic of the Stacktracer cog, at the guild level.

    Attributes
    -----------
    store
        The store used to interface with persistent data in a database-agnostic way.
    """

    store: StacktracerStore

    async def reply(self, ctx: GuildContext, content: str):
        """Wraps `Context.reply()` with some extension-default boilerplate."""
        await ctx.message.reply(
            content,
            allowed_mentions=AllowedMentions.none(),
        )

    async def show_guild_log_options(self, ctx: GuildContext):
        log_options = await self.store.get_guild_log_options(self.guild)
        if log_options:
            await self.reply(
                ctx,
                f"Error logging is configured for this guild: "
                + log_options.format(self.bot),
            )
        else:
            await self.reply(ctx, f"No error logging is configured for this guild.")

    async def set_guild_log_options(
        self,
        ctx: GuildContext,
        channel: TextChannel | Thread,
        stacktrace: Optional[bool],
        emoji: Optional[str],
        color: Optional[Color],
    ):
        new_log_options = LogOptions(
            channel=channel.id,
            stacktrace=stacktrace,
            emoji=emoji,
            color=color,
        )
        old_log_options = await self.store.set_guild_log_options(
            self.guild, new_log_options
        )
        if old_log_options:
            await self.reply(
                ctx,
                "Updated the error logging configuration for this guild from: "
                + old_log_options.format(self.bot)
                + f"\nto: "
                + new_log_options.format(self.bot),
            )
        else:
            await self.reply(
                ctx,
                "Set the error logging configuration for this guild: "
                + new_log_options.format(self.bot),
            )

    async def remove_guild_log_options(self, ctx: GuildContext):
        old_log_options = await self.store.set_guild_log_options(self.guild, None)
        if old_log_options:
            await self.reply(
                ctx,
                f"Removed the error logging configuration for this guild: "
                + old_log_options.format(self.bot),
            )
        else:
            await self.reply(ctx, f"No error logging is configured for this guild.")
