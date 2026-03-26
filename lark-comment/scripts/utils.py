"""
Utility functions for Lark Calendar skill.
Calendar API uses SECONDS timestamps.
"""

from datetime import datetime
from typing import Tuple


def datetime_to_calendar_timestamp(dt: datetime) -> str:
    """Convert datetime to Lark Calendar API timestamp (SECONDS).

    Calendar API uses second-level timestamps.
    Example: 1602504000 means 2020/10/12 20:00:00 (UTC +8)
    """
    return str(int(dt.timestamp()))


def datetime_to_timestamp_ms(dt: datetime) -> int:
    """Convert datetime to milliseconds (for list_events input)."""
    return int(dt.timestamp() * 1000)


def timestamp_ms_to_datetime(ts_ms: int) -> datetime:
    """Convert Lark API timestamp (milliseconds) to datetime."""
    return datetime.fromtimestamp(ts_ms / 1000)


def get_today_range_ms() -> Tuple[int, int]:
    """Get today's date range in timestamps (ms)."""
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return datetime_to_timestamp_ms(start_of_day), datetime_to_timestamp_ms(end_of_day)


def get_default_reminder() -> dict:
    """Get default reminder configuration (30 minutes before)."""
    return {"minutes": 30}


def format_timestamp_for_display(ts_ms: int) -> str:
    """Format timestamp for user-friendly display."""
    dt = timestamp_ms_to_datetime(ts_ms)
    return dt.strftime("%Y-%m-%d %H:%M")
