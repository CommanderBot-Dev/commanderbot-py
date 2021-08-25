from datetime import datetime, timezone
from typing import Any, Iterable, Tuple

from discord import Member

from commanderbot_ext.lib.value_formatter import ValueFormatter


def yield_member_date_fields(member: Member) -> Iterable[Tuple[str, Any]]:
    # member_joined_at
    joined_at: datetime = member.joined_at
    joined_at_ts = int(joined_at.replace(tzinfo=timezone.utc).timestamp())
    joined_at_str = f"<t:{joined_at_ts}:R>"
    yield "member_joined_at", ValueFormatter(joined_at_str)

    # member_for
    now = datetime.utcnow()
    member_for = now - member.joined_at
    member_for_str = f"{member_for.days} days"
    if member_for.days < 7:
        hh = int(member_for.total_seconds() / 3600)
        mm = int(member_for.total_seconds() / 60) % 60
        member_for_str = f"{hh} hours, {mm} minutes"
    yield "member_for", member_for_str

    # member_created_at
    created_at: datetime = member.created_at
    created_at_ts = int(created_at.replace(tzinfo=timezone.utc).timestamp())
    created_at_str = f"<t:{created_at_ts}:R>"
    yield "member_created_at", ValueFormatter(created_at_str)
