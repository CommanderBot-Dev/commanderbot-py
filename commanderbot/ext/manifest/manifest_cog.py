from typing import Optional

from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command

from commanderbot.ext.manifest.manifest import (
    Manifest,
    ModuleType,
    PackType,
    add_dependency,
)


class ManifestCog(Cog, name="commanderbot.ext.manifest"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.default_manifest_version = [1, 17, 0]

    def get_version(self, version_str: Optional[str]) -> list[int]:
        """
        Parses 'version_str' and either returns it as a list of 3 ints or
        returns the default min engine version
        """
        version: list[int] = self.default_manifest_version
        if version_str:
            found_version_numbers: list[int] = []
            for i in version_str.split("."):
                if not i.isnumeric():
                    break
                found_version_numbers.append(int(i))

            if len(found_version_numbers) == 3:
                version = found_version_numbers

        return version

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
        pack_name = name if name else "pack.name"
        pack_description = description if description else "pack.description"
        engine_version = self.get_version(min_engine_version)

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
