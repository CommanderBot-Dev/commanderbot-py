from collections import defaultdict
from importlib import import_module
from typing import Any, DefaultDict

from commanderbot_ext.ext.automod.automod_exception import AutomodException
from commanderbot_ext.lib import JsonObject

module_function_cache: DefaultDict[str, DefaultDict[str, Any]] = defaultdict(
    lambda: defaultdict(lambda: None)
)


def resolve_module_name(
    type_name: str,
    default_module_prefix: str,
) -> str:
    if "." in type_name:
        return type_name
    else:
        return f"{default_module_prefix}.{type_name}"


def resolve_module_function(
    type_name: str,
    default_module_prefix: str,
    function_name: str,
) -> Any:
    # determine the module name
    module_name = resolve_module_name(type_name, default_module_prefix)
    # check if it's already in our cache
    if func := module_function_cache[module_name][function_name]:
        return func
    # if not, attempt to resolve it dynamically
    module = import_module(module_name)
    func = getattr(module, function_name)
    module_function_cache[module_name][function_name] = func
    return func


class ModuleObjectDeserializationError(AutomodException):
    pass


class MissingTypeField(ModuleObjectDeserializationError):
    def __init__(self, readable_name: str):
        super().__init__(f"Missing {readable_name} type")


class InvalidModule(ModuleObjectDeserializationError):
    def __init__(self, readable_name: str, type_name: str, function_name: str):
        super().__init__(
            f"Unknown {readable_name} `{type_name}`:"
            + " the module could not be imported, or does not contain a valid"
            + f" `{function_name}` function"
        )


class MalformedData(ModuleObjectDeserializationError):
    def __init__(self, readable_name: str, type_name: str):
        super().__init__(
            f"Malformed {readable_name} `{type_name}`:"
            + " the data contains insufficient or malformed fields"
        )


def deserialize_module_object(
    data: JsonObject,
    readable_name: str,
    default_module_prefix: str,
    function_name: str,
) -> Any:
    # get the type name
    type_name = str(data.pop("type"))
    if not type_name:
        raise MissingTypeField(readable_name)
    # attempt to resolve the module function
    try:
        func = resolve_module_function(
            type_name=type_name,
            default_module_prefix=default_module_prefix,
            function_name=function_name,
        )
    except Exception as ex:
        raise InvalidModule(readable_name, type_name, function_name) from ex
    # attempt to call the function to create the object
    try:
        obj = func(data)
    except Exception as ex:
        raise MalformedData(readable_name, type_name) from ex
    return obj
