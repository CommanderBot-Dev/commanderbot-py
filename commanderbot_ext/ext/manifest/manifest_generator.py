import json
import uuid
from enum import Enum


class PackType(Enum):
    """
    Valid pack types for user input
    """

    ADDON = "addon"
    BEHAVIOR = "behavior"
    RESOURCE = "resource"
    SKIN = "skin"

    @classmethod
    def values(cls) -> list[str]:
        return [i.value for i in cls]


class ManifestType(Enum):
    """
    A manifest type. The value is used in the 'modules' array
    """

    DATA = "data"
    RESOURCE = "resources"
    SKIN = "skin_pack"


def generate_manifests(
    manifest_types: list[ManifestType],
    name: str,
    description: str,
    min_engine_version: list,
) -> list[str]:
    # Loop through all manifest
    generated_manifests: list[dict] = []
    for manifest_type in manifest_types:
        manifest: dict = {
            "format_version": 2,
            "header": {
                "name": name,
                "description": description,
                "uuid": str(uuid.uuid4()),
                "version": [1, 0, 0],
                "min_engine_version": min_engine_version,
            },
            "modules": [
                {
                    "type": manifest_type.value,
                    "uuid": str(uuid.uuid4()),
                    "version": [1, 0, 0],
                }
            ],
        }

        generated_manifests.append(manifest)

    # This is sort of a hack to make the behavior pack depend on the resource pack
    # when we're generating two manifests for an addon
    if len(generated_manifests) == 2:
        # Get uuid string of resource pack
        rp_uuid: str = generated_manifests[1]["header"]["uuid"]

        # Add dependencies list to behavior pack
        generated_manifests[0]["dependencies"] = [
            {"uuid": rp_uuid, "version": [1, 0, 0]}
        ]

    return [json.dumps(manifest, indent=4) for manifest in generated_manifests]
