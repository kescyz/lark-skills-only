"""
Utility functions for Lark Task skill.
Task API uses MILLISECONDS timestamps.
"""

from datetime import datetime
from typing import Tuple


def datetime_to_task_timestamp(dt: datetime) -> str:
    """Convert datetime to Lark Task API timestamp (MILLISECONDS).

    Task API uses millisecond-level timestamps.
    Example: 1675454764000
    """
    return str(int(dt.timestamp() * 1000))


def datetime_to_timestamp_ms(dt: datetime) -> int:
    """Convert datetime to milliseconds (int)."""
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


def format_timestamp_for_display(ts_ms: int) -> str:
    """Format timestamp for user-friendly display."""
    dt = timestamp_ms_to_datetime(ts_ms)
    return dt.strftime("%Y-%m-%d %H:%M")


def is_task_completed(task: dict) -> bool:
    """Check if a task/subtask is completed.

    IMPORTANT: Lark API returns completed_at as STRING, not integer!
    - completed_at = "0" means NOT completed
    - completed_at = "1767536341736" (timestamp > 0) means completed
    """
    completed_at = task.get("completed_at")
    if not completed_at:
        return False
    try:
        return int(completed_at) > 0
    except (ValueError, TypeError):
        return False
