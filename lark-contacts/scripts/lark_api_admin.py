"""Lark Contacts admin mixin: user and department CRUD.

For user search, use lark-token-manager MCP: search_users(query, field="all")
which returns lark_open_id, lark_user_id, name, email — no Lark API scope needed.
"""

from typing import Optional, Dict, Any, List

from lark_api_base import LarkAPIBase


class LarkContactsAdminMixin(LarkAPIBase):
    """Mixin for admin-level contacts ops: user/dept CRUD.

    Mixed into LarkContactsClient via multiple inheritance.
    NOTE: search_users removed — use lark-token-manager MCP search_users() instead.
    """

    # --- User CRUD ---

    def create_user(self, user_data: Dict) -> Dict:
        """Create new org member. tenant_access_token only.

        Required fields: name, mobile (or email for non-CN), department_ids, employee_type.

        Args:
            user_data: dict with user fields (name, mobile, email, department_ids,
                       employee_type, leader_user_id, etc.)

        Returns created user object.
        """
        result = self._call_api(
            "POST", "/contact/v3/users",
            data=user_data,
            params={"user_id_type": "user_id", "department_id_type": "department_id"}
        )
        return result.get("user") or {}

    def update_user(self, user_id: str, updates: Dict) -> Dict:
        """Partially update user fields (PATCH). tenant_access_token only.

        Args:
            user_id: user's open_id (default) or user_id
            updates: dict of fields to update (name, email, city, job_title, etc.)

        Returns updated user object.
        """
        result = self._call_api(
            "PATCH", f"/contact/v3/users/{user_id}",
            data=updates,
            params={"user_id_type": "open_id", "department_id_type": "open_department_id"}
        )
        return result.get("user") or {}

    def delete_user(self, user_id: str) -> bool:
        """Delete (offboard) a user. tenant_access_token only.

        Soft delete — user enters resigned state, data transferred to direct manager.
        App must have contact scope for all user's departments.

        Args:
            user_id: user's open_id (default id type)

        Returns True on success.
        """
        self._call_api(
            "DELETE", f"/contact/v3/users/{user_id}",
            params={"user_id_type": "open_id"}
        )
        return True

    # --- Department CRUD ---

    def create_department(self, name: str, parent_department_id: str,
                          leader_user_id: str = None, **kwargs) -> Dict:
        """Create a new department. tenant_access_token only.

        Args:
            name: department name (no slashes, unique among siblings)
            parent_department_id: parent dept ID; '0' for root-level
            leader_user_id: open_id of department head (optional)
            **kwargs: extra fields (order, unit_ids, create_group_chat, etc.)

        Returns created department object with department_id, open_department_id.
        """
        body: Dict[str, Any] = {
            "name": name,
            "parent_department_id": parent_department_id,
        }
        if leader_user_id:
            body["leader_user_id"] = leader_user_id
        body.update(kwargs)

        result = self._call_api(
            "POST", "/contact/v3/departments",
            data=body,
            params={"user_id_type": "open_id", "department_id_type": "department_id"}
        )
        return result.get("department") or {}

    def update_department(self, department_id: str, updates: Dict) -> Dict:
        """Partially update department fields (PATCH). tenant_access_token only.

        Args:
            department_id: dept ID matching department_id_type param
            updates: dict of fields to update (name, parent_department_id,
                     leader_user_id, order, leaders, etc.)

        Returns updated department object.
        """
        result = self._call_api(
            "PATCH", f"/contact/v3/departments/{department_id}",
            data=updates,
            params={"department_id_type": "department_id", "user_id_type": "open_id"}
        )
        return result.get("department") or {}

    def delete_department(self, department_id: str) -> bool:
        """Delete a department. tenant_access_token only.

        Department must be empty (no members, no sub-departments).

        Args:
            department_id: open_department_id (default) or custom department_id

        Returns True on success.
        """
        self._call_api(
            "DELETE", f"/contact/v3/departments/{department_id}",
            params={"department_id_type": "open_department_id"}
        )
        return True
