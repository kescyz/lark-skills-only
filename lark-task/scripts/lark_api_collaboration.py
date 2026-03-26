"""
Lark Task collaboration mixin — comments, reminders, dependencies.
Used via multiple inheritance by LarkTaskClient.
"""

from typing import Dict, Any, List
from lark_api_base import LarkAPIBase


class LarkTaskCollaborationMixin(LarkAPIBase):
    """Mixin for task collaboration APIs: comments, reminders, dependencies."""

    # Comment APIs
    def add_task_comment(self, task_guid: str, content: str) -> Dict[str, Any]:
        """Add a comment to a task. Returns created comment dict."""
        data = {
            "content": content,
            "resource_type": "task",
            "resource_id": task_guid,
        }
        result = self._call_api("POST", "/task/v2/comments", data=data)
        return result.get("comment", {})

    def list_task_comments(self, task_guid: str) -> List[Dict[str, Any]]:
        """List all comments on a task (paginated)."""
        params = {"resource_type": "task", "resource_id": task_guid}
        return self._fetch_all("/task/v2/comments", params=params)

    # Reminder APIs
    def add_task_reminder(self, task_guid: str, relative_fire_minute: int) -> Dict[str, Any]:
        """Add a reminder to a task. relative_fire_minute: minutes before due (0 = at due time).
        Note: task must have a due date set; max 1 reminder per task."""
        data = {"reminders": [{"relative_fire_minute": relative_fire_minute}]}
        result = self._call_api("POST", f"/task/v2/tasks/{task_guid}/add_reminders", data=data)
        reminders = result.get("task", {}).get("reminders", [])
        return reminders[0] if reminders else {}

    # Dependency APIs
    def add_task_dependency(self, task_guid: str, dependent_guid: str, dep_type: str = "prev") -> List[Dict[str, Any]]:
        """Add a dependency to a task.
        dep_type: 'prev' (this task depends on dependent) or 'next' (dependent depends on this task).
        Returns all dependencies after adding."""
        data = {"dependencies": [{"task_guid": dependent_guid, "type": dep_type}]}
        result = self._call_api("POST", f"/task/v2/tasks/{task_guid}/add_dependencies", data=data)
        return result.get("dependencies", [])

    def remove_task_dependency(self, task_guid: str, dependent_guid: str) -> bool:
        """Remove a dependency from a task by dependent task GUID."""
        data = {"dependencies": [{"task_guid": dependent_guid}]}
        self._call_api("POST", f"/task/v2/tasks/{task_guid}/remove_dependencies", data=data)
        return True

    # Tasklist detail API
    def get_tasklist_details(self, tasklist_guid: str) -> Dict[str, Any]:
        """Get full tasklist details including members, owner, and URL."""
        result = self._call_api("GET", f"/task/v2/tasklists/{tasklist_guid}")
        return result.get("tasklist", {})
