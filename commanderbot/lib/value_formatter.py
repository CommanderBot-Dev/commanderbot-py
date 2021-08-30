from typing import Any, Callable, Optional

__all__ = ("ValueFormatter",)


class ValueFormatter:
    def __init__(self, value: Any, formatter: Optional[Callable[[Any], str]] = None):
        self.value: Any = value
        self.formatter: Callable[[Any], str] = str

    def __str__(self) -> str:
        return self.formatter(self.value)
