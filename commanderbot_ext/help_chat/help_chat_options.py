from dataclasses import dataclass
from typing import Any, Optional

from commanderbot_lib.options.abc.cog_options import CogOptions


@dataclass
class HelpChatOptions(CogOptions):
    database: Optional[Any] = None
