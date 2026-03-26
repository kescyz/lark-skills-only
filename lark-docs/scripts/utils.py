"""
Utility functions for lark-docs skill.
"""

from datetime import datetime, timezone


# --- Timestamp Helpers ---

def datetime_to_timestamp(dt: datetime) -> str:
    """Convert datetime to MILLISECONDS string (13 digits)."""
    ts = int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
    return str(ts)


def get_today_range():
    """Get today's start and end as milliseconds timestamps."""
    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    multiplier = 1000
    return (
        int(start.timestamp() * multiplier),
        int(end.timestamp() * multiplier)
    )


def format_timestamp_for_display(ts) -> str:
    """Format timestamp for display: 'YYYY-MM-DD HH:MM'."""
    if not ts or ts == "0":
        return "N/A"
    divisor = 1000
    t = int(ts) / divisor
    return datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M")
