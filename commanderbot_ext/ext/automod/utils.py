from collections import defaultdict
from importlib import import_module
from typing import Any, DefaultDict

from commanderbot_ext.lib import JsonObject, ResponsiveException

module_function_cache: DefaultDict[str, DefaultDict[str, Any]] = defaultdict(
    lambda: defaultdict(lambda: None)
)


def resolve_module_function(module_name: str, function_name: str) -> Any:
    # check if it's already in our cache
    if func := module_function_cache[module_name][function_name]:
        return func
    # if not, attempt to resolve it dynamically
    module = import_module(module_name)
    func = getattr(module, function_name)
    module_function_cache[module_name][function_name] = func
    return func


class MissingTypeField(ResponsiveException):
    def __init__(self):
        super().__init__(f"Missing `type` field")


class InvalidModule(Exception):
    def __init__(self, module_name: str, function_name: str):
        super().__init__(
            f"Module `{module_name}` could not be imported,"
            + f" or does not contain a `{function_name}` function"
        )


class InvalidModuleFunction(Exception):
    def __init__(self, module_name: str, function_name: str):
        super().__init__(
            f"Function `{function_name}` in module `{module_name}` caused an error"
        )


def deserialize_module_object(
    data: JsonObject,
    default_module_prefix: str,
    function_name: str,
) -> Any:
    # get the type name
    type_name = str(data.pop("type"))
    if not type_name:
        raise MissingTypeField()
    # determine the module name
    module_name = type_name
    if "." not in type_name:
        module_name = f"{default_module_prefix}.{type_name}"
    # attempt to resolve the module function
    try:
        func = resolve_module_function(module_name, function_name)
    except Exception as ex:
        raise InvalidModule(module_name, function_name) from ex
    # attempt to call the function to create the object
    try:
        obj = func(data)
    except Exception as ex:
        raise InvalidModuleFunction(module_name, function_name) from ex
    return obj
