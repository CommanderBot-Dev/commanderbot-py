from typing import Any, Type


class MalformedData(Exception):
    def __init__(self, cls: Type, data: Any):
        super().__init__(f"Cannot create `{cls.__name__}` from `{type(data).__name__}`")
