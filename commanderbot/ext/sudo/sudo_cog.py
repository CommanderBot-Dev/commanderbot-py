import platform
from logging import Logger, getLogger
from typing import Optional

import psutil
from discord import AppInfo, Embed, HTTPException, Object
from discord.app_commands import AppCommand
from discord.ext.commands import Bot, Cog, Context, group

from commanderbot.ext.sudo.sudo_data import SyncType, CogUsesStore
from commanderbot.ext.sudo.sudo_exceptions import (
    CogHasNoStore,
    SyncError,
    SyncUnknownGuild,
    UnknownCog,
    UnsupportedStoreExport,
)
from commanderbot.lib import JsonFileDatabaseAdapter, checks
from commanderbot.lib.dialogs import ConfirmationResult, confirm_with_reaction
from commanderbot.lib.json import json_dumps
from commanderbot.lib.utils import SizeUnit, bytes_to, pointer_size, str_to_file


class SudoCog(Cog, name="commanderbot.ext.sudo"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.log: Logger = getLogger(self.qualified_name)

        # Grab the current process and get its CPU usage to throw away the initial 0% usage.
        self.process: psutil.Process = psutil.Process()
        self.process.cpu_percent()

    @group(name="sudo", brief="Commands for bot maintainers")
    @checks.guild_only()
    @checks.is_owner()
    async def cmd_sudo(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_sudo)

    @cmd_sudo.command(name="appinfo", brief="Show application info")
    async def cmd_appinfo(self, ctx: Context):
        # Get app info
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

        # Get basic info on the running process
        uname = platform.uname()
        ptr_size: int = pointer_size()

        architecture: str = "x86" if ptr_size == 32 else f"x{ptr_size}"
        cpu_usage: float = self.process.cpu_percent() / psutil.cpu_count()
        memory_usage: float = bytes_to(
            self.process.memory_full_info().uss, SizeUnit.MEGABYTE, binary=True
        )

        # Create embed fields
        commands_field = (
            f"Total: `{len(self.bot.commands)}`",
            f"Prefix: `{self.bot.command_prefix}`",
        )

        app_commands_field = (
            f"Total: `{len(self.bot.tree.get_commands())}`",
            f"Global Commands: {has_app_commands}",
        )

        system_field = (
            f"OS: `{uname.system} {architecture}`",
            f"Version: `{uname.version}`",
        )

        process_field = (
            f"CPU: `{cpu_usage:.2f}%`",
            f"RAM: `{memory_usage:.2f} MiB`",
        )

        fields = {
            "Owner": f"{app.owner.mention} ({app.owner})",
            "Flags": f"`{app.flags.value}`",
            "Message Content": message_content_enabled,
            "Guild Members": guild_members_enabled,
            "Presence": presence_enabled,
            "Commands": "\n".join(commands_field),
            "App Commands": "\n".join(app_commands_field),
            "System": "\n".join(system_field),
            "Process": "\n".join(process_field),
        }

        # Create embed and add fields
        embed: Embed = Embed(
            title=app.name, description=app.description, color=0x00ACED
        )

        embed.set_thumbnail(url=app.icon.url if app.icon else None)
        for k, v in fields.items():
            embed.add_field(name=k, value=v)

        await ctx.reply(embed=embed, mention_author=False)

    @cmd_sudo.command(name="shutdown", brief="Shutdowns the bot")
    async def cmd_sudo_shutdown(self, ctx: Context):
        result = await confirm_with_reaction(
            self.bot, ctx, "Are you sure you want to shutdown the bot?"
        )
        match result:
            case ConfirmationResult.YES:
                await ctx.reply("😴 Shutting down...", mention_author=False)
                await self.bot.close()
            case (ConfirmationResult.NO | ConfirmationResult.NO_RESPONSE):
                await ctx.reply("🙂 Continuing...", mention_author=False)

    @cmd_sudo.command(name="export", brief="Exports a cog's store if it has one")
    async def cmd_sudo_export(self, ctx: Context, cog: str):
        # Try to get the cog
        found_cog = self.bot.get_cog(cog)
        if not found_cog:
            raise UnknownCog(cog)

        # Try to get the database adapter if it exists
        if isinstance(found_cog, CogUsesStore):
            db = found_cog.store.db
            match db:
                case JsonFileDatabaseAdapter():
                    await self._export_json_store(ctx, found_cog, db)
                case _:
                    raise UnsupportedStoreExport(db)
        else:
            raise CogHasNoStore(found_cog)

    async def _export_json_store(
        self, ctx: Context, cog: Cog, db: JsonFileDatabaseAdapter
    ):
        data = await db.get_cache()
        data = db.serializer(data)
        await ctx.reply(
            content=f"Exported Json store for `{cog.qualified_name}`",
            file=str_to_file(json_dumps(data), f"{cog.qualified_name}.json"),
            mention_author=False,
        )

    @cmd_sudo.group(name="sync", brief="Sync app commands")
    async def cmd_sudo_sync(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_sudo_sync)

    @cmd_sudo_sync.command(name="global", brief="Sync global app commands")
    async def cmd_sudo_sync_global(self, ctx: Context):
        self.log.info("Started syncing app commands globally...")
        await ctx.message.add_reaction("⏲️")

        synced_commands: list[AppCommand] = await self.bot.tree.sync()

        assert(self.bot.user)
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
            assert(self.bot.user)
            await ctx.message.remove_reaction("⏲️", self.bot.user)

        # Send message with sync results and print it in the log too
        self.log.info(f"Synced {len(synced_commands)} app commands to guild {guild.id}")
        await ctx.reply(
            f"Synced `{len(synced_commands)}` app commands to {syncing_to_msg}",
            mention_author=False,
        )
