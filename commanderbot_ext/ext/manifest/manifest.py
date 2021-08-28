import json
from dataclasses import dataclass
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


@dataclass
class Manifest:
    """
    A complete manifest
    """

    module_type: ModuleType
    name: str
    description: str
    min_engine_version: list[int]
    authors: list[str]
    url: str

    pack_uuid: str
    module_uuid: str
    dependency_uuid: Optional[str] = None

    def as_json(self) -> str:
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
                ],

        # Add metadata if it exists
        if self.authors or self.url:
            manifest["metadata"] = {}
            if self.authors:
                manifest["metadata"]["authors"] = self.authors
            if self.url:
                manifest["metadata"]["url"] = self.url

        # Serialize object as a json string
        return json.dumps(manifest, indent=4)

    def type(self) -> str:
        if self.module_type == ModuleType.DATA:
            return "Behavior"
        elif self.module_type == ModuleType.RESOURCE:
            return "Resource"
        elif self.module_type == ModuleType.SKIN:
            return "Skin"
        return ""
