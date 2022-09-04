from enum import Enum, auto


class SyncType(Enum):
    SYNC_ONLY = auto()
    COPY = auto()
    REMOVE = auto()
