from datetime import datetime
from typing import AsyncIterable, List, Optional, Protocol, Set, Tuple

from discord import Guild

from commanderbot_ext.lib import ResponsiveException


class FaqException(ResponsiveException):
    pass


class FaqKeyAlreadyExists(FaqException):
    def __init__(self, faq_key: str):
        self.faq_key: str = faq_key
        super().__init__(f"FAQ `{faq_key}` already exists")


class FaqAliasUnavailable(FaqException):
    def __init__(self, faq_alias: str):
        self.faq_alias: str = faq_alias
        super().__init__(f"FAQ alias `{faq_alias}` is unavailable")


class NoSuchFaq(FaqException):
    def __init__(self, faq_key: str):
        self.faq_key: str = faq_key
        super().__init__(f"No such FAQ `{faq_key}`")


class FaqEntry(Protocol):
    key: str
    added_on: datetime
    modified_on: datetime
    hits: int
    content: str
    link: Optional[str]
    aliases: Set[str]
    tags: Set[str]

    @property
    def sorted_aliases(self) -> List[str]:
        ...

    @property
    def sorted_tags(self) -> List[str]:
        ...


class FaqStore(Protocol):
    """
    Abstracts the data storage and persistence of the FAQ cog.
    """

    async def get_faq_entries(self, guild: Guild) -> List[FaqEntry]:
        ...

    async def require_faq_entry(self, guild: Guild, faq_key: str) -> FaqEntry:
        ...

    def query_faq_entries(
        self, guild: Guild, faq_query: str
    ) -> AsyncIterable[FaqEntry]:
        ...

    async def scan_for_faqs(self, guild: Guild, text: str) -> Optional[List[FaqEntry]]:
        ...

    async def increment_faq_hits(self, faq_entry: FaqEntry):
        ...

    async def add_faq(
        self, guild: Guild, faq_key: str, link: str, content: str
    ) -> FaqEntry:
        ...

    async def remove_faq(self, guild: Guild, faq_key: str) -> FaqEntry:
        ...

    async def modify_faq_content(
        self, guild: Guild, faq_key: str, content: str
    ) -> FaqEntry:
        ...

    async def modify_faq_link(
        self, guild: Guild, faq_key: str, link: Optional[str]
    ) -> FaqEntry:
        ...

    async def modify_faq_aliases(
        self, guild: Guild, faq_key: str, aliases: Tuple[str, ...]
    ) -> FaqEntry:
        ...

    async def modify_faq_tags(
        self, guild: Guild, faq_key: str, tags: Tuple[str, ...]
    ) -> FaqEntry:
        ...

    async def configure_prefix(self, guild: Guild, prefix: Optional[str]):
        ...

    async def configure_match(self, guild: Guild, match: Optional[str]):
        ...
