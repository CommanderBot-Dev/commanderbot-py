import uuid
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
    def from_str(cls, pack_type_str: str) -> Optional["PackType"]:
        try:
            return cls(pack_type_str.strip().lower())
        except ValueError:
            return None

    @classmethod
    def values(cls) -> list[str]:
        return [i.value for i in cls]


class ModuleType(Enum):
    DATA = "data"
    RESOURCE = "resources"
    SKIN = "skin_pack"


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    def as_list(self) -> list[int]:
        return [self.major, self.minor, self.patch]

    @classmethod
    def from_str(cls, version_str: str) -> Optional["Version"]:
        version_numbers: list[int] = []
        for i in version_str.strip().split(".")[:3]:
            if i.isnumeric():
                version_numbers.append(int(i))

        if len(version_numbers) == 3:
            return cls(*version_numbers)
        else:
            return None


class Manifest:
    """
    A complete manifest
    """

    def __init__(
        self,
        module_type: ModuleType,
        name: str,
        description: str,
        min_engine_version: Version,
    ):
        self.module_type: ModuleType = module_type
        self.name: str = name
        self.description: str = description
        self.min_engine_version: Version = min_engine_version

        self.pack_uuid: str = str(uuid.uuid4())
        self.module_uuid: str = str(uuid.uuid4())
        self.dependency_uuid: Optional[str] = None

    def common_name(self) -> str:
        """
        Common name for a pack that has a manifest with the stored module type
        """
        match self.module_type:
            case ModuleType.DATA:
                return "Behavior Pack"
            case ModuleType.RESOURCE:
                return "Resource Pack"
            case ModuleType.SKIN:
                return "Skin Pack"
            case _:
                return "Unknown Pack"

    def as_dict(self) -> dict:
        """
        Turns manifest contents into a dict
        """
        manifest = {
            "format_version": 2,
            "header": {
                "name": self.name,
                "description": self.description,
                "uuid": self.pack_uuid,
                "version": [1, 0, 0],
                "min_engine_version": self.min_engine_version.as_list(),
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
        return manifest


def add_dependency(manifest: Manifest, dependent_manifest: Manifest):
    """
    Adds 'dependent_manifest' as a dependency to 'manifest'
    """
    manifest.dependency_uuid = dependent_manifest.pack_uuid
