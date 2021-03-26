import json
from dataclasses import dataclass, field
from typing import Any, Dict

from commanderbot_lib.logging import Logger, get_logger

from commanderbot_ext._lib.database_options import JsonFileDatabaseOptions


@dataclass
class JsonFileDatabaseAdapter:
    options: JsonFileDatabaseOptions

    log: Logger = field(init=False)

    def __post_init__(self):
        self.log = get_logger(f"{self.__class__.__name__}@{self.options.path.name}")

    async def read(self) -> Dict[str, Any]:
        # TODO Async file I/O. #optimize
        try:
            with open(self.options.path) as fp:
                data = json.load(fp)
            return data
        except FileNotFoundError as ex:
            if self.options.no_init:
                raise ex
            else:
                self.log.warning(
                    f"Initializing database file because it doesn't already exist: {self.options.path}"
                )
                self.options.path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.options.path, "w") as fp:
                    json.dump({}, fp)
                return {}

    async def write(self, data: Dict[str, Any]):
        # TODO Async file I/O. #optimize
        with open(self.options.path, "w") as fp:
            json.dump(data, fp, indent=self.options.indent)
