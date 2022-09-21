from logging import Logger, getLogger
from typing import Optional

from discord import AppInfo, Object, Embed, HTTPException
from discord.app_commands import AppCommand
from discord.ext.commands import Bot, Cog, Context, group

from commanderbot.ext.sudo.sudo_data import SyncType
from commanderbot.ext.sudo.sudo_exceptions import SyncError, SyncUnknownGuild
from commanderbot.lib import checks


class SudoCog(Cog, name="commanderbot.ext.sudo"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.log: Logger = getLogger(self.qualified_name)

    @group(name="sudo", brief="Commands for bot maintainers")
    @checks.guild_only()
    @checks.is_owner()
    async def cmd_sudo(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_sudo)

    @cmd_sudo.command(name="appinfo", brief="Show application info")
    async def cmd_appinfo(self, ctx: Context):
        app: AppInfo = await self.bot.application_info()

        has_app_commands: str = "✅" if app.flags.app_commands_badge else "❌"
        message_content_enabled: str = "❌"
        if app.flags.gateway_message_content:
            message_content_enabled = "✅"
        elif app.flags.gateway_message_content_limited:
            message_content_enabled = "✅ (Limited)"

        guild_members_enabled: str = "❌"
        if app.flags.gateway_guild_members:
            guild_members_enabled = "✅"
        elif app.flags.gateway_guild_members_limited:
            guild_members_enabled = "✅ (Limited)"

        presence_enabled: str = "❌"
        if app.flags.gateway_presence:
            presence_enabled = "✅"
        elif app.flags.gateway_presence_limited:
            presence_enabled = "✅ (Limited)"

        embed: Embed = Embed(
            title=app.name, description=app.description, color=0x00ACED
        )

        embed.set_thumbnail(url=app.icon.url if app.icon else None)
        embed.add_field(name="Owner", value=f"{app.owner.mention} ({app.owner})")
        embed.add_field(name="Flags", value=app.flags.value)
        embed.add_field(name="App Commands", value=has_app_commands)
        embed.add_field(name="Message Content", value=message_content_enabled)
        embed.add_field(name="Guild Members", value=guild_members_enabled)
        embed.add_field(name="Presence", value=presence_enabled)

        await ctx.reply(embed=embed, mention_author=False)

    @cmd_sudo.group(name="sync", brief="Sync app commands")
    async def cmd_sudo_sync(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_sudo_sync)

    @cmd_sudo_sync.command(name="global", brief="Sync global app commands")
    async def cmd_sudo_sync_global(self, ctx: Context):
        self.log.info("Started syncing app commands globally...")
        await ctx.message.add_reaction("⏲️")

        synced_commands: list[AppCommand] = await self.bot.tree.sync()

        await ctx.message.add_reaction("✅")
        await ctx.message.remove_reaction("⏲️", self.bot.user)

        self.log.info(f"Synced {len(synced_commands)} app commands globally")
        await ctx.reply(
            f"Synced `{len(synced_commands)}` app commands globally",
            mention_author=False,
        )

    @cmd_sudo_sync.group(name="guild", brief="Sync app commands to a guild")
    async def cmd_sudo_sync_guild(self, ctx: Context):
        # If we didn't invote a subcommand, sync the current guild the normal way
        if not ctx.invoked_subcommand:
            if sync_to := self._get_current_guild(ctx):
                await self._sync_guild_app_commands(ctx, sync_to)
            else:
                raise SyncUnknownGuild(sync_to)

    @cmd_sudo_sync_guild.command(name="sync_only", brief="Sync app commands to a guild")
    async def cmd_sudo_sync_guild_sync_only(
        self, ctx: Context, guild: Optional[Object] = None
    ):
        if sync_to := guild if guild else self._get_current_guild(ctx):
            await self._sync_guild_app_commands(ctx, sync_to, SyncType.SYNC_ONLY)
        else:
            raise SyncUnknownGuild(sync_to)

    @cmd_sudo_sync_guild.command(
        name="copy", brief="Copy and sync app commands to a guild"
    )
    async def cmd_sudo_sync_guild_copy(
        self, ctx: Context, guild: Optional[Object] = None
    ):
        if sync_to := guild if guild else self._get_current_guild(ctx):
            await self._sync_guild_app_commands(ctx, sync_to, SyncType.COPY)
        else:
            raise SyncUnknownGuild(sync_to)

    @cmd_sudo_sync_guild.command(
        name="remove", brief="Remove app commands from a guild"
    )
    async def cmd_sudo_sync_guild_remove(
        self, ctx: Context, guild: Optional[Object] = None
    ):
        if sync_to := guild if guild else self._get_current_guild(ctx):
            await self._sync_guild_app_commands(ctx, sync_to, SyncType.REMOVE)
        else:
            raise SyncUnknownGuild(sync_to)

    def _get_current_guild(self, ctx: Context) -> Optional[Object]:
        """
        Gets the current guild from `ctx` if it exists
        """
        return Object(id=ctx.guild.id) if ctx.guild else None

    async def _sync_guild_app_commands(
        self, ctx: Context, guild: Object, sync_type: SyncType = SyncType.SYNC_ONLY
    ):
        self.log.info("Started syncing app commands to a guild...")
        await ctx.message.add_reaction("⏲️")

        # Create message used for saying if we're syncing with the current guild or with a guild ID
        is_current_guild: bool = guild == self._get_current_guild(ctx)
        syncing_to_msg: str = (
            "the current guild" if is_current_guild else f"guild `{guild.id}`"
        )

        # Try to sync app commands
        synced_commands: list[AppCommand] = []
        try:
            match sync_type:
                case SyncType.SYNC_ONLY:
                    synced_commands = await self.bot.tree.sync(guild=guild)
                case SyncType.COPY:
                    self.bot.tree.copy_global_to(guild=guild)
                    synced_commands = await self.bot.tree.sync(guild=guild)
                case SyncType.REMOVE:
                    self.bot.tree.clear_commands(guild=guild)
                    synced_commands = await self.bot.tree.sync(guild=guild)

            await ctx.message.add_reaction("✅")
        except HTTPException as ex:
            await ctx.message.add_reaction("🔥")

            self.log.warn(
                f"Unable to sync app commands with guild {guild.id}: {ex.text}"
            )
            raise SyncError(guild, ex.text)
        finally:
            await ctx.message.remove_reaction("⏲️", self.bot.user)

        # Send message with sync results and print it in the log too
        self.log.info(f"Synced {len(synced_commands)} app commands to guild {guild.id}")
        await ctx.reply(
            f"Synced `{len(synced_commands)}` app commands to {syncing_to_msg}",
            mention_author=False,
        )
