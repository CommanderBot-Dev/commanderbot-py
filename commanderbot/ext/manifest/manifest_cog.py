from typing import Optional

import aiohttp
from discord import Embed
from discord.ext import tasks
from discord.ext.commands import Bot, Cog, Context, command

from commanderbot.ext.manifest.manifest import (
    Manifest,
    ModuleType,
    PackType,
    Version,
    add_dependency,
)

DEFAULT_MIN_ENGINE_VERSION = Version(1, 17, 0)
VERSION_URL = (
    "https://raw.githubusercontent.com/Ersatz77/bedrock-data/master/VERSION.txt"
)


class ManifestCog(Cog, name="commanderbot.ext.manifest"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.default_min_engine_version: Version = DEFAULT_MIN_ENGINE_VERSION

        # Start task loop
        self.update_min_engine_version.start()

    def cog_unload(self):
        # Stop task loop
        self.update_min_engine_version.cancel()

    @tasks.loop(seconds=5.0)
    async def update_min_engine_version(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(VERSION_URL, raise_for_status=True) as response:
                    if version := self._parse_version(await response.text()):
                        self.default_min_engine_version = version

        except Exception:
            pass

        print(self.default_min_engine_version.as_list())

    def _parse_version(self, version_str: str) -> Optional[Version]:
        valid_values: list[int] = []
        for i in version_str.strip().split(".")[:3]:
            if i.isnumeric():
                valid_values.append(int(i))

        if len(valid_values) == 3:
            return Version.from_list(valid_values)
        else:
            return None

    @command(name="manifest", brief="Generate a Bedrock manifest")
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
        pack_type = pack_type.strip().lower()
        if pack_type == PackType.ADDON.value:
            modules.append(ModuleType.DATA)
            modules.append(ModuleType.RESOURCE)
        elif pack_type == PackType.BEHAVIOR.value or pack_type == PackType.DATA.value:
            modules.append(ModuleType.DATA)
        elif pack_type == PackType.RESOURCE.value:
            modules.append(ModuleType.RESOURCE)
        elif pack_type == PackType.SKIN.value:
            modules.append(ModuleType.SKIN)
        else:
            available_pack_types = [f"`{i}`" for i in PackType.values()]
            await ctx.message.reply(
                f"**{pack_type}** is not a valid pack type\n"
                f"Available pack types: {' '.join(available_pack_types)}"
            )
            return

        # Parse optional arguments
        pack_name: str = name if name else "pack.name"
        pack_description: str = description if description else "pack.description"
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
            if manifest.module_type == ModuleType.DATA:
                common_name = "Behavior pack"
            elif manifest.module_type == ModuleType.RESOURCE:
                common_name = "Resource pack"
            elif manifest.module_type == ModuleType.SKIN:
                common_name = "Skin pack"

            formatted_manifest_json: str = f"```json\n{manifest.as_json()}\n```"
            description_text += f"**{common_name}**\n{formatted_manifest_json}\n"

        manifest_embed.description = description_text
        await ctx.send(embed=manifest_embed)
