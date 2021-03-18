from dataclasses import dataclass
from typing import Any, Optional

from commanderbot_lib.options.abc.cog_options import CogOptions


@dataclass
class FaqOptions(CogOptions):
    database: Optional[Any] = None
    prefix: Optional[str] = None
