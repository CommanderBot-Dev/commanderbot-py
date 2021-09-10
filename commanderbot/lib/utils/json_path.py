from __future__ import annotations

from enum import Enum
from typing import Any, cast

from jsonpath_ng import JSONPath as JsonPath
from jsonpath_ng import parse

from commanderbot.lib.responsive_exception import ResponsiveException

__all__ = (
    "JsonPath",
    "JsonPathOp",
    "parse_json_path_op",
    "parse_json_path",
    "query_json_path",
    "update_json_with_path",
)


class JsonPathOp(Enum):
    set = "set"
    merge = "merge"
    append = "append"
    prepend = "prepend"


def parse_json_path_op(op: str) -> JsonPathOp:
    try:
        return JsonPathOp[op]
    except:
        raise ResponsiveException(f"No such operation: `{op}`")


def parse_json_path(path: str) -> JsonPath:
    try:
        return cast(JsonPath, parse(path))
    except:
        raise ResponsiveException(f"Malformed JSON path: `{path}`")


def query_json_path(target: Any, path: JsonPath) -> Any:
    nodes = list(path.find(target))
    if not nodes:
        raise ResponsiveException(f"No such value: `{path}`")
    if len(nodes) == 1:
        return nodes[0].value
    values = [node.value for node in nodes]
    return values


def update_json_with_path(target: Any, path: JsonPath, op: JsonPathOp, value: Any):
    if op == JsonPathOp.set:
        path.update_or_create(target, value)
    elif op == JsonPathOp.merge:
        if not isinstance(value, dict):
            raise ValueError(f"Expected `dict`, got `{type(target).__name__}`")
        for node in path.find_or_create(target):
            if isinstance(node.value, dict):
                node.value.update(value)
    elif op == JsonPathOp.append:
        for node in path.find_or_create(target):
            if isinstance(node.value, list):
                node.value.append(value)
    elif op == JsonPathOp.prepend:
        for node in path.find_or_create(target):
            if isinstance(node.value, list):
                node.value.insert(0, value)
    else:
        raise ResponsiveException(f"Unsupported operation: `{op.value}`")
