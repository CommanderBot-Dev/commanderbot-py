import asyncio
import json
from pathlib import Path
from typing import Any

from commanderbot_ext.lib.extended_json_encoder import ExtendedJsonEncoder
from commanderbot_ext.lib.types import JsonObject


def to_data(obj: Any) -> Any:
    # TODO There's got to be a direct way to do this... #optimize
    return json.loads(json.dumps(obj, cls=ExtendedJsonEncoder))


def json_load(path: Path) -> JsonObject:
    with open(path) as fp:
        data = json.load(fp)
    return data


async def json_load_async(path: Path) -> JsonObject:
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, json_load, path)
    return data


def json_dump(
    data: JsonObject,
    path: Path,
    mkdir: bool = False,
    indent: int = None,
):
    if mkdir:
        path.parent.mkdir(parents=True, exist_ok=True)
    # NOTE Serialize the JSON first, otherwise invalid data may corrupt the file.
    output = json.dumps(data, indent=indent, cls=ExtendedJsonEncoder)
    with open(path, "w") as fp:
        fp.write(output)


async def json_dump_async(
    data: JsonObject,
    path: Path,
    mkdir: bool = False,
    indent: int = None,
):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, json_dump, data, path, mkdir, indent)
