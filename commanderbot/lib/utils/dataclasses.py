import dataclasses
import typing
from typing import Union

__all__ = ("is_field_optional",)


def is_field_optional(field: dataclasses.Field) -> bool:
    field_type_origin = typing.get_origin(field.type)
    field_type_args = typing.get_args(field.type)
    is_union = field_type_origin is Union
    is_nullable = type(None) in field_type_args
    return is_union and is_nullable
