import json
from datetime import datetime
from logging import Logger, getLogger
from typing import Optional

import aiohttp
from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command, group
from discord.ext.tasks import loop

from commanderbot.ext.manifest.manifest_data import (
    Manifest,
    ModuleType,
    PackType,
    Version,
    add_dependency,
)
from commanderbot.ext.manifest.manifest_exceptions import InvalidPackType
from commanderbot.lib import checks
from commanderbot.lib.utils.datetimes import datetime_to_int
from commanderbot.lib.utils.utils import str_to_file, utcnow_aware

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
        self.previous_request_date: Optional[datetime] = None
        self.previous_status_code: Optional[int] = None

        self.version_url: Optional[str] = options.get("version_url")
        if not self.version_url:
            self.log.warn(
                "No version URL was given in the bot config. "
                f"Using {DEFAULT_ENGINE_VERSION.as_list()} for 'min_engine_version'."
            )

        self.update_default_engine_version.start()

    def cog_unload(self):
        self.update_default_engine_version.cancel()

    @loop(hours=1)
    async def update_default_engine_version(self):
        """
        A task that updates 'self.default_engine_version'. If there was an issue parsing
        the version, the attribute isn't modified. The patch version will always be set
        to 0.
        """
        # Return early if no URL was given
        if not self.version_url:
            return

        # Request version
        async with aiohttp.ClientSession() as session:
            async with session.get(self.version_url) as response:
                self.previous_request_date = utcnow_aware()
                self.previous_status_code = response.status
                if response.status == 200:
                    if version := Version.from_str(await response.text()):
                        version.patch = 0
                        self.default_engine_version = version

    @command(name="manifest", brief="Generate a Bedrock manifest", help=HELP)
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
                raise InvalidPackType(pack_type)

        # Parse optional arguments
        pack_name: str = name if name else DEFAULT_NAME
        pack_description: str = description if description else DEFAULT_DESCRIPTION
        engine_version: Version = self.default_engine_version
        if version := Version.from_str(str(min_engine_version)):
            engine_version = version

        # Create a list of manifests from modules
        manifests: list[Manifest] = [
            Manifest(module, pack_name, pack_description, engine_version)
            for module in modules
        ]

        # If we're generating a complete addon, make the behavior pack dependent
        # on the resource pack
        if len(manifests) == 2:
            add_dependency(manifests[0], manifests[1])

        # Reply to the member with uploaded files
        for manifest in manifests:
            manifest_json: str = json.dumps(manifest.as_dict(), indent=4)
            await ctx.message.reply(
                content=f"**{manifest.common_name()}**",
                file=str_to_file(manifest_json, "manifest.json"),
                mention_author=False,
            )

    @group(name="manifests", brief="Manage manifests")
    @checks.is_administrator()
    async def cmd_manifests(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_manifests)

    @cmd_manifests.command(name="status", brief="Show the status of version requests")
    async def cmd_manifests_status(self, ctx: Context):
        # Format optional attributes
        url: str = "None set"
        previous_request_ts: str = "?"
        next_request_ts: str = "?"
        previous_status_code: str = "?"
        self.update_default_engine_version
        if version_url := self.version_url:
            url = version_url
            if dt := self.previous_request_date:
                previous_request_ts = f"<t:{datetime_to_int(dt)}:R>"

            if dt := self.update_default_engine_version.next_iteration:
                next_request_ts = f"<t:{datetime_to_int(dt)}:R>"

            if status := self.previous_status_code:
                previous_status_code = f"`{status}`"

        # Create embed
        status_embed: Embed = Embed(title=self.qualified_name, color=0x00ACED)
        status_embed.add_field(name="Version URL", value=url, inline=False)
        status_embed.add_field(name="Previous request", value=previous_request_ts)
        status_embed.add_field(name="Next request", value=next_request_ts)
        status_embed.add_field(name="Previous status code", value=previous_status_code)
        status_embed.add_field(
            name="Min engine version",
            value=f"`{self.default_engine_version.as_list()}`",
        )

        await ctx.send(embed=status_embed)

    @cmd_manifests.command(name="update", brief="Manually request the version")
    async def cmd_manifests_update(self, ctx: Context):
        if self.version_url:
            self.update_default_engine_version.restart()
            await ctx.message.add_reaction("✅")
        else:
            await ctx.message.add_reaction("❌")
