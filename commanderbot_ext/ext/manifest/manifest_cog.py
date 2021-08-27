from typing import Optional

from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command

from commanderbot_ext.ext.manifest.manifest_generator import (
    ManifestType,
    PackType,
    generate_manifests,
)


class ManifestCog(Cog, name="commanderbot_ext.ext.manifest"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.default_manifest_version = [1, 17, 0]

    def get_manifests(self, pack_type: str) -> list[ManifestType]:
        """
        Parses 'pack_type' and returns the list of manifests to generate
        """
        pack_type = pack_type.strip().lower()
        if pack_type == PackType.ADDON.value:
            return [ManifestType.DATA, ManifestType.RESOURCE]
        elif pack_type == PackType.BEHAVIOR.value:
            return [ManifestType.DATA]
        elif pack_type == PackType.RESOURCE.value:
            return [ManifestType.RESOURCE]
        elif pack_type == PackType.SKIN.value:
            return [ManifestType.SKIN]
        else:
            return []

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

    @command(name="manifest", brief="Generates a Bedrock manifest")
    async def cmd_manifest(
        self,
        ctx: Context,
        pack_type: str,
        name: Optional[str],
        description: Optional[str],
        min_engine_version: Optional[str],
    ):
        # Parse arguments
        requested: list[ManifestType] = self.get_manifests(pack_type.strip().lower())
        engine_version: list[int] = self.get_version(min_engine_version)
        pack_name: str = str(name) if name else "pack.name"
        pack_description: str = str(description) if description else "pack.description"

        # If no manifests were requested, reply with an error and return
        if not requested:
            available_pack_types: list[str] = [f"`{i}`" for i in PackType.values()]
            await ctx.reply(
                f"**{pack_type}** is not a valid pack type\n"
                f"Available pack types: {' '.join(available_pack_types)}"
            )
            return

        # Generate manifests
        generated: list[str] = generate_manifests(
            requested, pack_name, pack_description, engine_version
        )

        # Create embed and send it to the user
        manifest_embed = Embed(color=0x00ACED)
        if len(generated) == 2:
            manifest_embed.title = f"Addon Manifest"
            bp_text = f"**Behavior Pack Manifest**\n```json\n{generated[0]}\n```"
            rp_text = f"**Resource Pack Manifest**\n```json\n{generated[1]}\n```"
            manifest_embed.description = f"{bp_text}\n{rp_text}"
        else:
            manifest_embed.title = f"{pack_type.title()} Pack Manifest"
            manifest_embed.description = f"```json\n{generated[0]}\n```"

        await ctx.send(embed=manifest_embed)
