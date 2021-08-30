from datetime import datetime, timezone
from typing import Any, Iterable, Tuple

from discord import Member

from commanderbot.lib.value_formatter import ValueFormatter


def yield_member_date_fields(prefix: str, member: Member) -> Iterable[Tuple[str, Any]]:
    # joined_at
    joined_at = member.joined_at
    if isinstance(joined_at, datetime):
        joined_at_ts = int(joined_at.timestamp())
        joined_at_str = f"<t:{joined_at_ts}:R>"
        joined_at_value = ValueFormatter(joined_at_str)
    else:
        joined_at_value = "Unknown"
    yield f"{prefix}_joined_at", joined_at_value

    # member_for
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    if isinstance(joined_at, datetime):
        member_for = now - joined_at
        member_for_str = f"{member_for.days} days"
        if member_for.days < 7:
            hh = int(member_for.total_seconds() / 3600)
            mm = int(member_for.total_seconds() / 60) % 60
            member_for_str = f"{hh} hours, {mm} minutes"
        member_for_value = member_for_str
    else:
        member_for_value = "Unknown"
    yield f"{prefix}_member_for", member_for_value

    # created_at
    created_at: datetime = member.created_at
    created_at_ts = int(created_at.replace(tzinfo=timezone.utc).timestamp())
    created_at_str = f"<t:{created_at_ts}:R>"
    yield f"{prefix}_created_at", ValueFormatter(created_at_str)
