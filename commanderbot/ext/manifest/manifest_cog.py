from datetime import date, datetime, timezone
from logging import Logger, getLogger
from typing import Optional

import aiohttp
from discord import Embed
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Cog, Context

from commanderbot.ext.manifest.manifest_data import (
    Manifest,
    ModuleType,
    PackType,
    Version,
    add_dependency,
)
from commanderbot.lib import checks

DEFAULT_NAME = "pack.name"
DEFAULT_DESCRIPTION = "pack.description"
DEFAULT_ENGINE_VERSION = Version(1, 17, 0)

HELP = "\n".join(
    (
        f"<pack_type>: ({'|'.join(PackType.values())})",
        f"[name]: The name of your pack",
        f"[description]: A short description for your pack",
        f"[min_engine_version]: The minimum version of Minecraft that this pack was made for",
    )
)


class ManifestCog(Cog, name="commanderbot.ext.manifest"):
    def __init__(self, bot: Bot, **options):
        self.bot: Bot = bot
        self.log: Logger = getLogger(self.qualified_name)

        self.default_engine_version: Version = DEFAULT_ENGINE_VERSION
        self.requested_at: Optional[datetime] = None
        self.version_url: Optional[str] = options.get("version_url")
        if not self.version_url:
            self.log.warn(
                "No version URL was given in the bot config. "
                f"Using {DEFAULT_ENGINE_VERSION.as_list()} for 'min_engine_version'."
            )

        # Start task loop
        self.update_default_engine_version.start()

    def cog_unload(self):
        # Stop task loop
        self.update_default_engine_version.cancel()

    @tasks.loop(minutes=30)
    async def update_default_engine_version(self):
        """
        A task that updates 'self.default_engine_version'. If there was an issue
        parsing the version, the attribute isn't modified.
        """
        # Return early if no URL was given
        if not self.version_url:
            return

        # Request version
        self.requested_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.version_url, raise_for_status=True
                ) as response:
                    if version := Version.from_str(await response.text()):
                        self.default_engine_version = version

        except Exception:
            pass

    @commands.command(name="manifest", brief="Generate a Bedrock manifest", help=HELP)
    async def cmd_manifest(
        self,
        ctx: Context,
        pack_type: str,
        name: Optional[str],
        description: Optional[str],
        min_engine_version: Optional[str],
    ):
        # Parse required pack type argument and create a list of modules from it
        modules: list[ModuleType] = []
        match PackType.from_str(pack_type):
            case PackType.ADDON:
                modules.append(ModuleType.DATA)
                modules.append(ModuleType.RESOURCE)
            case (PackType.BEHAVIOR | PackType.DATA):
                modules.append(ModuleType.DATA)
            case PackType.RESOURCE:
                modules.append(ModuleType.RESOURCE)
            case PackType.SKIN:
                modules.append(ModuleType.SKIN)
            case _:
                available_pack_types = [f"`{i}`" for i in PackType.values()]
                await ctx.message.reply(
                    f"**{pack_type}** is not a valid pack type\n"
                    f"Available pack types: {', '.join(available_pack_types)}"
                )
                return

        # Parse optional arguments
        pack_name: str = name if name else DEFAULT_NAME
        pack_description: str = description if description else DEFAULT_DESCRIPTION
        engine_version: Version = self.default_engine_version
        if version := Version.from_str(str(min_engine_version)):
            engine_version = version

        # Create a list of manifests from modules
        manifests: list[Manifest] = []
        for module in modules:
            manifests.append(
                Manifest(module, pack_name, pack_description, engine_version)
            )

        # If we're generating a complete addon, make the behavior pack dependent
        # on the resource pack
        if len(manifests) == 2:
            add_dependency(manifests[0], manifests[1])

        # Send embed
        manifest_embed = Embed(title="Generated manifest", color=0x00ACED)
        description_text = ""
        for manifest in manifests:
            # Get the common name for a manifest using each kind of module
            common_name: str = ""
            match manifest.module_type:
                case  ModuleType.DATA:
                    common_name = "Behavior pack"
                case  ModuleType.RESOURCE:
                    common_name = "Resource pack"
                case ModuleType.SKIN:
                    common_name = "Skin pack"

            formatted_manifest_json: str = f"```json\n{manifest.as_json()}\n```"
            description_text += f"**{common_name}**\n{formatted_manifest_json}\n"

        manifest_embed.description = description_text
        await ctx.send(embed=manifest_embed)

    @commands.group(name="manifests", brief="Manage manifests")
    @checks.is_administrator()
    async def cmd_manifests(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_manifests)

    @cmd_manifests.command(name="status", brief="Shows the status of this extension")
    async def cmd_manifests_status(self, ctx: Context):
        # Format optional attributes
        url = self.version_url if self.version_url else "None set"
        request_ts: str = "No requests have been made"
        if dt := self.requested_at:
            request_ts = f"<t:{int(dt.timestamp())}:R>"

        # Create embed
        status_embed: Embed = Embed(title=self.qualified_name, color=0x00ACED)
        status_embed.add_field(name="Version URL", value=url, inline=False)
        status_embed.add_field(name="Last requested", value=request_ts)
        status_embed.add_field(
            name="Min engine version",
            value=f"`{self.default_engine_version.as_list()}`",
        )

        await ctx.send(embed=status_embed)
