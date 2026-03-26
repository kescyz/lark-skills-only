"""
Lark Task API client.
Handles Tasks, Subtasks, Tasklists, Sections, Custom Fields, Contact, Comments, Reminders, and Dependencies.
"""

from typing import Optional, Dict, Any, List
from lark_api_base import LarkAPIBase
from lark_api_collaboration import LarkTaskCollaborationMixin


class LarkTaskClient(LarkTaskCollaborationMixin, LarkAPIBase):
    """Client for Lark Task APIs (tasks, subtasks, tasklists, sections, custom fields)."""

    # Task APIs
    def list_tasks(self, completed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """List tasks. Set completed=False for pending tasks only."""
        params = {}
        if completed is not None:
            params["completed"] = "true" if completed else "false"
        data = self._call_api("GET", "/task/v2/tasks", params=params)
        return data.get("items", [])

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create task. Defaults to assigning to current user if no members specified."""
        if "members" not in task_data:
            if self.user_open_id:
                task_data["members"] = [{"id": self.user_open_id, "role": "assignee"}]
        return self._call_api("POST", "/task/v2/tasks", data=task_data)

    def update_task(self, task_guid: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update task."""
        data = {"task": task_data, "update_fields": list(task_data.keys())}
        return self._call_api("PATCH", f"/task/v2/tasks/{task_guid}", data=data)

    def delete_task(self, task_guid: str) -> bool:
        """Delete task."""
        self._call_api("DELETE", f"/task/v2/tasks/{task_guid}")
        return True

    def get_task(self, task_guid: str) -> Dict[str, Any]:
        """Get task details."""
        data = self._call_api("GET", f"/task/v2/tasks/{task_guid}")
        return data.get("task", {})

    # Subtask APIs
    def list_subtasks(self, task_guid: str) -> List[Dict[str, Any]]:
        """List subtasks of a task."""
        data = self._call_api("GET", f"/task/v2/tasks/{task_guid}/subtasks")
        return data.get("items", [])

    def create_subtask(self, task_guid: str, subtask_data: Dict[str, Any], parent_members: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Create subtask under a task. Inherits members from parent if not specified."""
        if "members" not in subtask_data:
            if parent_members:
                subtask_data["members"] = parent_members
            else:
                parent_task = self.get_task(task_guid)
                parent_task_members = parent_task.get("members", [])
                if parent_task_members:
                    subtask_data["members"] = parent_task_members
                else:
                    if self.user_open_id:
                        subtask_data["members"] = [{"id": self.user_open_id, "role": "assignee"}]
        return self._call_api("POST", f"/task/v2/tasks/{task_guid}/subtasks", data=subtask_data)

    # Tasklist APIs
    def list_tasklists(self) -> List[Dict[str, Any]]:
        """List all tasklists."""
        data = self._call_api("GET", "/task/v2/tasklists")
        return data.get("items", [])

    def create_tasklist(self, name: str, members: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Create tasklist."""
        tasklist_data = {"name": name}
        if members:
            tasklist_data["members"] = members
        return self._call_api("POST", "/task/v2/tasklists", data=tasklist_data)

    def delete_tasklist(self, tasklist_guid: str) -> bool:
        """Delete tasklist."""
        self._call_api("DELETE", f"/task/v2/tasklists/{tasklist_guid}")
        return True

    def get_tasklist_tasks(self, tasklist_guid: str, completed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get all tasks in a tasklist."""
        params = {}
        if completed is not None:
            params["completed"] = "true" if completed else "false"
        data = self._call_api("GET", f"/task/v2/tasklists/{tasklist_guid}/tasks", params=params)
        return data.get("items", [])

    # Contact API
    def get_user_by_id(self, user_id: str, id_type: str = "open_id") -> Optional[Dict[str, Any]]:
        """Get user info by ID using Contact API."""
        try:
            params = {"user_id_type": id_type}
            data = self._call_api("GET", f"/contact/v3/users/{user_id}", params=params)
            return data.get("user")
        except Exception:
            return None

    # Section APIs
    def create_section(self, name: str, resource_type: str, resource_id: Optional[str] = None, insert_before: Optional[str] = None, insert_after: Optional[str] = None) -> Dict[str, Any]:
        """Create a section in a resource (tasklist or my_tasks)."""
        data: Dict[str, Any] = {"name": name, "resource_type": resource_type}
        if resource_id:
            data["resource_id"] = resource_id
        if insert_before:
            data["insert_before"] = insert_before
        if insert_after:
            data["insert_after"] = insert_after
        return self._call_api("POST", "/task/v2/sections", data=data)

    def get_section(self, section_guid: str) -> Dict[str, Any]:
        """Get section details."""
        data = self._call_api("GET", f"/task/v2/sections/{section_guid}")
        return data.get("section", {})

    def update_section(self, section_guid: str, name: Optional[str] = None, insert_before: Optional[str] = None, insert_after: Optional[str] = None) -> Dict[str, Any]:
        """Update section name or position."""
        section_data: Dict[str, Any] = {}
        update_fields = []
        if name:
            section_data["name"] = name
            update_fields.append("name")
        if insert_before:
            section_data["insert_before"] = insert_before
            update_fields.append("insert_before")
        if insert_after:
            section_data["insert_after"] = insert_after
            update_fields.append("insert_after")
        data = {"section": section_data, "update_fields": update_fields}
        return self._call_api("PATCH", f"/task/v2/sections/{section_guid}", data=data)

    def delete_section(self, section_guid: str) -> bool:
        """Delete section. Tasks move to default section."""
        self._call_api("DELETE", f"/task/v2/sections/{section_guid}")
        return True

    def list_sections(self, resource_type: str, resource_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all sections in a resource."""
        params: Dict[str, Any] = {"resource_type": resource_type}
        if resource_id:
            params["resource_id"] = resource_id
        return self._fetch_all("/task/v2/sections", params=params)

    def list_section_tasks(self, section_guid: str, completed: Optional[bool] = None, created_from: Optional[str] = None, created_to: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all tasks in a section."""
        params: Dict[str, Any] = {}
        if completed is not None:
            params["completed"] = "true" if completed else "false"
        if created_from:
            params["created_from"] = created_from
        if created_to:
            params["created_to"] = created_to
        return self._fetch_all(f"/task/v2/sections/{section_guid}/tasks", params=params)

    # Custom Field APIs
    def create_custom_field(self, name: str, field_type: str, resource_type: str = "tasklist", resource_id: Optional[str] = None, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a custom field."""
        data: Dict[str, Any] = {"name": name, "type": field_type, "resource_type": resource_type}
        if resource_id:
            data["resource_id"] = resource_id
        if settings:
            data.update(settings)
        return self._call_api("POST", "/task/v2/custom_fields", data=data)

    def get_custom_field(self, custom_field_guid: str) -> Dict[str, Any]:
        """Get custom field details."""
        data = self._call_api("GET", f"/task/v2/custom_fields/{custom_field_guid}")
        return data.get("custom_field", {})

    def update_custom_field(self, custom_field_guid: str, name: Optional[str] = None, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update custom field name or settings."""
        field_data: Dict[str, Any] = {}
        update_fields = []
        if name:
            field_data["name"] = name
            update_fields.append("name")
        if settings:
            for key, value in settings.items():
                field_data[key] = value
                update_fields.append(key)
        data = {"custom_field": field_data, "update_fields": update_fields}
        return self._call_api("PATCH", f"/task/v2/custom_fields/{custom_field_guid}", data=data)

    def list_custom_fields(self, resource_type: Optional[str] = None, resource_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all custom fields, optionally filtered by resource."""
        params: Dict[str, Any] = {}
        if resource_type:
            params["resource_type"] = resource_type
        if resource_id:
            params["resource_id"] = resource_id
        return self._fetch_all("/task/v2/custom_fields", params=params)

    def add_custom_field_to_resource(self, custom_field_guid: str, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """Add custom field to a resource (link to tasklist)."""
        data = {"resource_type": resource_type, "resource_id": resource_id}
        return self._call_api("POST", f"/task/v2/custom_fields/{custom_field_guid}/add", data=data)

    def remove_custom_field_from_resource(self, custom_field_guid: str, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """Remove custom field from a resource (unlink from tasklist)."""
        data = {"resource_type": resource_type, "resource_id": resource_id}
        return self._call_api("POST", f"/task/v2/custom_fields/{custom_field_guid}/remove", data=data)
