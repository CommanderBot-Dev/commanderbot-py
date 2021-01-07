from dataclasses import dataclass
from typing import Any, Optional

from commanderbot_lib.options.abc.cog_options import CogOptions


@dataclass
class HelpChatOptions(CogOptions):
    database: Optional[Any] = None
    nom_summary_batch_length: int = 2000
