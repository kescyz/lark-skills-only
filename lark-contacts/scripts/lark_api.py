"""Lark Contacts API client. People, departments, user groups.
Uses tenant_access_token for all operations (app-level access to org directory)."""

from typing import Optional, Dict, Any, List

from lark_api_base import LarkAPIBase
from lark_api_admin import LarkContactsAdminMixin


class LarkContactsClient(LarkContactsAdminMixin, LarkAPIBase):
    """Client for Lark Contact v3 API — org directory, departments, user groups.

    Uses tenant_access_token (like lark-messenger). All contact read/write ops
    work with tenant token. Only search_departments requires user_access_token
    (not supported here — use get_org_chart for tree browsing instead).
    """

    def __init__(self, access_token: str, user_open_id: str = "", user_id: str = None):
        """Initialize with tenant_access_token from MCP get_tenant_token().

        Args:
            access_token: tenant_access_token from MCP get_tenant_token()
            user_open_id: current user's open_id (for context, from MCP whoami)
            user_id: current user's user_id (optional)
        """
        super().__init__(access_token=access_token, user_open_id=user_open_id, user_id=user_id)

    # --- People ---

    def get_user(self, user_id: str, id_type: str = "open_id") -> Dict[str, Any]:
        """Get full user profile (23+ fields incl. city, join_time, employee_type, status).

        Args:
            user_id: user identifier (open_id, union_id, or user_id)
            id_type: open_id | union_id | user_id (default: open_id)

        Returns user object with fields based on app's contact scopes.
        Note: department_path field NOT available with tenant_token.
        """
        return self._call_api(
            "GET", f"/contact/v3/users/{user_id}",
            params={"user_id_type": id_type}
        ).get("user", {})

    def list_department_members(self, dept_id: str, page_size: int = 50) -> List[Dict[str, Any]]:
        """List all users in a department (paginated). Root dept = '0'.

        Returns list of full user objects. Filtered by app's contact scope.
        """
        return self._fetch_all(
            "/contact/v3/users/find_by_department",
            params={"department_id": dept_id, "user_id_type": "open_id"},
            page_size=page_size
        )

    def batch_resolve_ids(self, emails: List[str] = None,
                          mobiles: List[str] = None,
                          include_resigned: bool = False) -> Dict[str, Any]:
        """Resolve emails/mobiles to Lark user IDs. Max 50 each.

        Returns: {"user_list": [{"user_id": open_id, "email": ..., "status": ...}]}
        Note: use personal email, not corporate email.
        """
        body: Dict[str, Any] = {"include_resigned": include_resigned}
        if emails:
            body["emails"] = emails[:50]
        if mobiles:
            body["mobiles"] = mobiles[:50]
        return self._call_api(
            "POST", "/contact/v3/users/batch_get_id",
            data=body, params={"user_id_type": "open_id"}
        )

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Convenience: resolve email -> open_id -> full user profile.

        Returns full user object or None if not found.
        """
        result = self.batch_resolve_ids(emails=[email])
        user_list = result.get("user_list", [])
        if not user_list:
            return None
        open_id = user_list[0].get("user_id")
        if not open_id:
            return None
        return self.get_user(open_id, id_type="open_id")

    # --- Departments ---

    def get_department(self, dept_id: str, id_type: str = "department_id") -> Dict[str, Any]:
        """Get department info: name, leader, member_count, chat_id, parent_id.

        Args:
            dept_id: department identifier. Root dept = '0'.
            id_type: department_id | open_department_id (default: department_id)
        """
        return self._call_api(
            "GET", f"/contact/v3/departments/{dept_id}",
            params={"user_id_type": "open_id", "department_id_type": id_type}
        ).get("department", {})

    def get_org_chart(self, dept_id: str = "0", fetch_child: bool = False,
                      page_size: int = 50) -> List[Dict[str, Any]]:
        """Get direct (or recursive) child departments. Root dept = '0'.

        Args:
            dept_id: parent department ID (default: '0' = root)
            fetch_child: True for recursive tree, False for direct children only.
                         Tenant token: limited by app's contact scope.
            page_size: max 50 per page
        """
        params: Dict[str, Any] = {
            "department_id_type": "department_id",
            "user_id_type": "open_id",
        }
        if fetch_child:
            params["fetch_child"] = "true"
        return self._fetch_all(
            f"/contact/v3/departments/{dept_id}/children",
            params=params,
            page_size=page_size
        )

    def get_department_path(self, dept_id: str,
                            id_type: str = "department_id") -> List[Dict[str, Any]]:
        """Get ancestor chain from dept up to root (within app's contact scope).

        Args:
            dept_id: department identifier
            id_type: department_id | open_department_id (default: department_id)
        Returns list of department objects ordered from child to root.
        """
        data = self._call_api(
            "GET", "/contact/v3/departments/parent",
            params={
                "department_id": dept_id,
                "department_id_type": id_type,
                "user_id_type": "open_id",
            }
        )
        return data.get("items", [])

    # --- Groups ---

    def list_groups(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """List all user groups in the company.

        page_size max 100. Returns list of {id, name} objects.
        """
        return self._fetch_all(
            "/contact/v3/group/simplelist",
            page_size=page_size
        )

    def get_group(self, group_id: str) -> Dict[str, Any]:
        """Get user group detail: name, description, type, member_count."""
        return self._call_api(
            "GET", f"/contact/v3/group/{group_id}"
        ).get("group", {})

    def list_group_members(self, group_id: str,
                           member_id_type: str = "open_id") -> List[Dict[str, Any]]:
        """List members of a user group.

        Args:
            group_id: group identifier
            member_id_type: open_id | union_id | user_id (default: open_id)
        Returns list of {member_id, member_id_type, member_type} objects.
        """
        return self._fetch_all(
            f"/contact/v3/group/{group_id}/member/simplelist",
            params={"member_id_type": member_id_type}
        )
