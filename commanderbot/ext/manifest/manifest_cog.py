from typing import Optional

import aiohttp
from discord import Embed
from discord.ext import tasks
from discord.ext.commands import Bot, Cog, Context, command

from commanderbot.ext.manifest.manifest_data import (
    Manifest,
    ModuleType,
    PackType,
    Version,
    add_dependency,
)

VERSION_URL = (
    "https://raw.githubusercontent.com/Ersatz77/bedrock-data/master/VERSION.txt"
)

DEFAULT_NAME = "pack.name"
DEFAULT_DESCRIPTION = "pack.description"
DEFAULT_MIN_ENGINE_VERSION = Version(1, 17, 0)

HELP = "\n".join((
    f"<pack_type>: ({'|'.join(PackType.values())})",
    f"[name]: The name of your pack",
    f"[description]: A short description for your pack",
    f"[min_engine_version]: The minimum version of Minecraft that this pack was made for",
))


class ManifestCog(Cog, name="commanderbot.ext.manifest"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.default_min_engine_version: Version = DEFAULT_MIN_ENGINE_VERSION

        # Start task loop
        self.update_default_min_engine_version.start()

    def cog_unload(self):
        # Stop task loop
        self.update_default_min_engine_version.cancel()

    @tasks.loop(hours=1)
    async def update_default_min_engine_version(self):
        """
        A task that updates 'self.default_min_engine_version'. If there was an issue
        parsing the version, the attribute isn't modified.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(VERSION_URL, raise_for_status=True) as response:
                    if version := self._parse_version(await response.text()):
                        self.default_min_engine_version = version

        except Exception:
            pass

    def _parse_version(self, version_str: str) -> Optional[Version]:
        """
        Parses 'version_str' and tries to create a Version out of the first 3 numbers.
        """
        version_numbers: list[int] = []
        for i in version_str.strip().split(".")[:3]:
            if i.isnumeric():
                version_numbers.append(int(i))

        if len(version_numbers) == 3:
            return Version(*version_numbers)
        else:
            return None

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
                available_pack_types = [f"`{i}`" for i in PackType.values()]
                await ctx.message.reply(
                    f"**{pack_type}** is not a valid pack type\n"
                    f"Available pack types: {', '.join(available_pack_types)}"
                )
                return

        # Parse optional arguments
        pack_name: str = name if name else DEFAULT_NAME
        pack_description: str = description if description else DEFAULT_DESCRIPTION
        
        engine_version: Version = self.default_min_engine_version
        if version := self._parse_version(str(min_engine_version)):
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
