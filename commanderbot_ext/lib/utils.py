import asyncio
import json
from pathlib import Path
from typing import Any, AsyncIterable, List, Mapping, Optional, Type, TypeVar

from commanderbot import CommanderBotBase
from discord.ext.commands import Bot, Cog

from commanderbot_ext.lib.types import JsonObject


def check_commander_bot(bot: Bot) -> Optional[CommanderBotBase]:
    if isinstance(bot, CommanderBotBase):
        return bot


def add_configured_cog(bot: Bot, ext_name: str, cog_class: Type[Cog]):
    cog = None
    if cb := check_commander_bot(bot):
        if options := cb.get_extension_options(ext_name):
            cog = cog_class(bot, **options)
    if not cog:
        cog = cog_class(bot)
    bot.add_cog(cog)


def is_bot(bot: Bot, user: Any) -> bool:
    return user == bot.user or getattr(user, "bot")


def dict_without_nones(d: Optional[Mapping[str, Any]] = None, **kwargs):
    dd = dict(d, **kwargs) if d else kwargs
    return {k: v for k, v in dd.items() if v is not None}


def dict_without_falsies(d: Optional[Mapping[str, Any]] = None, **kwargs):
    dd = dict(d, **kwargs) if d else kwargs
    return {k: v for k, v in dd.items() if v}


T = TypeVar("T")


async def async_expand(it: AsyncIterable[T]) -> List[T]:
    return [value async for value in it]


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
    with open(path, "w") as fp:
        json.dump(data, fp, indent=indent)


async def json_dump_async(
    data: JsonObject,
    path: Path,
    mkdir: bool = False,
    indent: int = None,
):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, json_dump, data, path, mkdir, indent)
