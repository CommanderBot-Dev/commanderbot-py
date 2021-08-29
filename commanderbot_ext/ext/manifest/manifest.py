import json
import uuid
from enum import Enum
from typing import Optional


class PackType(Enum):
    ADDON = "addon"
    BEHAVIOR = "behavior"
    DATA = "data"
    RESOURCE = "resource"
    SKIN = "skin"

    @classmethod
    def values(cls) -> list[str]:
        return [i.value for i in cls]


class ModuleType(Enum):
    DATA = "data"
    RESOURCE = "resources"
    SKIN = "skin_pack"


class Manifest:
    """
    A complete manifest
    """

    def __init__(
        self,
        module_type: ModuleType,
        name: str,
        description: str,
        min_engine_version: list[int],
    ):
        self.module_type: ModuleType = module_type
        self.name: str = name
        self.description: str = description
        self.min_engine_version: list[int] = min_engine_version

        self.pack_uuid: str = str(uuid.uuid4())
        self.module_uuid: str = str(uuid.uuid4())
        self.dependency_uuid: Optional[str] = None

    def as_json(self) -> str:
        """
        Serializes this manifest as a Json string
        """
        manifest = {
            "format_version": 2,
            "header": {
                "name": self.name,
                "description": self.description,
                "uuid": self.pack_uuid,
                "version": [1, 0, 0],
                "min_engine_version": self.min_engine_version,
            },
            "modules": [
                {
                    "type": self.module_type.value,
                    "uuid": self.module_uuid,
                    "version": [1, 0, 0],
                }
            ],
        }

        # Add dependency if the UUID exists
        if self.dependency_uuid:
            manifest["dependencies"] = [
                {
                    "uuid": self.dependency_uuid,
                    "version": [1, 0, 0],
                }
            ]

        # Serialize object as a json string
        return json.dumps(manifest, indent=4)


def add_dependency(manifest: Manifest, dependent_manifest: Manifest):
    """
    Adds 'dependent_manifest' as a dependency to 'manifest'
    """
    manifest.dependency_uuid = dependent_manifest.pack_uuid
