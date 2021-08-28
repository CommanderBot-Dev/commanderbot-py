import re
import uuid
from typing import Optional

import discord
from discord.ext.commands import Bot, Cog, Context, command

from commanderbot_ext.ext.manifest.manifest import Manifest, ModuleType, PackType


class ManifestCog(Cog, name="commanderbot_ext.ext.manifest"):
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

    @staticmethod
    def get_authors(authors_str: Optional[str]) -> list[str]:
        authors: list[str] = []
        if authors_str:
            for author in re.split("\\s|,", authors_str):
                authors.append(author.strip())
        return authors

    @command(name="manifest", brief="Generates a Bedrock manifest")
    async def cmd_manifest(
        self,
        ctx: Context,
        pack_type: str,
        name: Optional[str],
        description: Optional[str],
        min_engine_version: Optional[str],
        authors: Optional[str],
        url: Optional[str],
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
            await ctx.reply(
                f"**{pack_type}** is not a valid pack type\n"
                f"Available pack types: {' '.join(available_pack_types)}"
            )
            return

        # Parse optional arguments
        pack_name = name if name else "pack.name"
        pack_description = description if description else "pack.description"
        engine_version = self.get_version(min_engine_version)
        pack_authors: list[str] = self.get_authors(authors)
        pack_url: str = url if url else ""

        # Create a list of manifests from arguments
        manifests: list[Manifest] = []
        for module in modules:
            manifests.append(
                Manifest(
                    module,
                    pack_name,
                    pack_description,
                    engine_version,
                    pack_authors,
                    pack_url,
                    str(uuid.uuid4()),
                    str(uuid.uuid4()),
                )
            )

        # If we're generating a complete addon, make the behavior pack dependent
        # on the resource pack
        if len(manifests) == 2:
            manifests[0].dependency_uuid = manifests[1].pack_uuid

        # Send embed
        manifest_embed = discord.Embed(title="Generated manifest", color=0x00ACED)
        description_text = ""
        for manifest in manifests:
            description_text += (
                f"**{manifest.type()} Pack**\n```json\n{manifest.as_json()}\n```\n"
            )
        manifest_embed.description = description_text
        await ctx.send(embed=manifest_embed)
