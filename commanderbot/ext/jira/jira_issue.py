from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class StatusColor(Enum):
    UNKNOWN = 0x00ACED
    MEDIUM_GRAY = 0x42526E
    BLUE_GRAY = 0x42526E
    GREEN = 0x00875A
    WARM_RED = 0xDE350B
    YELLOW = 0x0052CC
    BROWN = 0xFF991F

    @classmethod
    def from_str(cls, color: str):
        color = color.replace("-", "_").upper()
        try:
            return cls[color]
        except KeyError:
            return cls.UNKNOWN


@dataclass
class JiraIssue:
    url: str
    icon_url: str
    issue_id: str
    summary: str
    assignee: str
    created_on: datetime
    status: str
    status_color: StatusColor
    resolution: str
    since_version: str
    fix_version: str
    votes: int

    @property
    def fields(self) -> dict:
        return {
            "Assigned to": self.assignee,
            "Created": f"<t:{int(self.created_on.timestamp())}:R>",
            "Status": self.status,
            "Resolution": self.resolution,
            "Since version": self.since_version,
            "Fix version": self.fix_version,
            "Votes": self.votes,
        }
