from dataclasses import dataclass
from typing import Any

from commanderbot_lib.options.abc.cog_options import CogOptions


@dataclass
class FaqOptions(CogOptions):
    database: Any = None
    prefix: str = None
