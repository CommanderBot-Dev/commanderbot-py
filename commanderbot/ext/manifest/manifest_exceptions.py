from commanderbot.ext.manifest.manifest_data import PackType
from commanderbot.lib.responsive_exception import ResponsiveException


class ManifestError(ResponsiveException):
    pass


class InvalidPackType(ManifestError):
    def __init__(self, given_pack_type: str):
        self.given_pack_type = given_pack_type
        super().__init__(
            f"**{self.given_pack_type}** is not a valid pack type\n"
            f"Available pack types: {', '.join([f'`{i}`' for i in PackType.values()])}"
        )
