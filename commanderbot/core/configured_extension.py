from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, TypeVar

from commanderbot.lib import FromDataMixin

ST = TypeVar("ST")


@dataclass
class ConfiguredExtension(FromDataMixin):
    name: str
    disabled: bool = False
    options: Optional[Dict[str, Any]] = None

    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, str):
            # Extensions starting with a `!` are disabled.
            disabled = data.startswith("!")
            name = data[1:] if disabled else data
            return cls(name=name, disabled=disabled)
        elif isinstance(data, dict):
            return cls(**data)
