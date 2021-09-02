from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass
class EventData:
    name: str
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]

    def format_codeblock(self) -> str:
        lines = [
            "```python",
            repr(self),
            "```",
        ]
        return "\n".join(lines)
