from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

__all__ = ("SQLDatabaseAdapter",)


class SQLDatabaseAdapter(Protocol):
    def connect(self) -> AsyncConnection:
        ...

    def begin(self) -> AsyncConnection:
        ...

    def session(self) -> AsyncSession:
        ...
