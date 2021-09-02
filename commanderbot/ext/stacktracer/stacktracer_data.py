from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, DefaultDict, Optional, Type, TypeVar

from discord import Guild

from commanderbot.lib import FromDataMixin, GuildID, JsonSerializable, LogOptions
from commanderbot.lib.utils import dict_without_ellipsis, dict_without_falsies

ST = TypeVar("ST")


@dataclass
class StacktracerGuildData(JsonSerializable, FromDataMixin):
    log_options: Optional[LogOptions] = None

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, dict):
            log_options = LogOptions.from_field_optional(data, "log")
            return cls(log_options=log_options)

    # @implements JsonSerializable
    def to_json(self) -> Any:
        # Omit empty log options.
        data = dict_without_ellipsis(log=self.log_options or ...)

        return data

    def set_log_options(
        self, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        old_value = self.log_options
        self.log_options = log_options
        return old_value


def _guilds_defaultdict_factory() -> DefaultDict[GuildID, StacktracerGuildData]:
    return defaultdict(lambda: StacktracerGuildData())


# @implements StacktracerStore
@dataclass
class StacktracerData(JsonSerializable, FromDataMixin):
    """
    Implementation of `StacktracerStore` using an in-memory object hierarchy.
    """

    # Global log options configured by bot owners.
    log_options: Optional[LogOptions] = None

    # Per-guild log options configured by admins (or owners).
    guilds: DefaultDict[GuildID, StacktracerGuildData] = field(
        default_factory=_guilds_defaultdict_factory
    )

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, dict):
            # Construct global log options.
            log_options = LogOptions.from_field_optional(data, "log_options")

            # Construct guild data.
            guilds = _guilds_defaultdict_factory()
            for raw_guild_id, raw_guild_data in data.get("guilds", {}).items():
                guild_id = int(raw_guild_id)
                guilds[guild_id] = StacktracerGuildData.from_data(raw_guild_data)

            return cls(
                log_options=log_options,
                guilds=guilds,
            )

    # @implements JsonSerializable
    def to_json(self) -> Any:
        guilds = {
            str(guild_id): guild_data.to_json()
            for guild_id, guild_data in self.guilds.items()
        }

        # Omit empty guilds.
        trimmed_guilds = dict_without_falsies(guilds)

        # Omit empty fields.
        data = dict_without_ellipsis(
            log_options=self.log_options or ...,
            guilds=trimmed_guilds or ...,
        )

        return data

    # @implements StacktracerStore
    async def get_global_log_options(self) -> Optional[LogOptions]:
        return self.log_options

    # @implements StacktracerStore
    async def set_global_log_options(
        self, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        old_value = self.log_options
        self.log_options = log_options
        return old_value

    # @implements StacktracerStore
    async def get_guild_log_options(self, guild: Guild) -> Optional[LogOptions]:
        return self.guilds[guild.id].log_options

    # @implements StacktracerStore
    async def set_guild_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        return self.guilds[guild.id].set_log_options(log_options)
