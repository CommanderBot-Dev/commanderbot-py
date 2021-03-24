from dataclasses import dataclass
from typing import Any


@dataclass
class JsonFileDatabase:
    async def read(self) -> Any:
        raise NotImplementedError()

    async def write(self, data: Any):
        raise NotImplementedError()
