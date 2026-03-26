"""Lark Base advanced permission management — roles and members."""

from lark_api_base import LarkAPIBase


class LarkRoleClient(LarkAPIBase):
    """Custom role CRUD. Max 30 roles per Base.
    Prerequisite: enable advanced permissions via update_app(is_advanced=True)."""

    def list_roles(self, app_token, page_size=30):
        """List custom roles. Max 30 roles per Base, page_size max 30."""
        data = self._call_api(
            "GET", f"/bitable/v1/apps/{app_token}/roles",
            params={"page_size": page_size}
        )
        return data.get("items", data.get("roles", []))

    def create_role(self, app_token, role_name, table_roles=None,
                    block_roles=None):
        """Create custom role with row/column permissions.
        table_roles: [{table_name, table_perm, rec_rule?, field_perm?}]
        block_roles: [{block_id, block_type, block_perm}]"""
        data = {"role_name": role_name}
        if table_roles:
            data["table_roles"] = table_roles
        if block_roles:
            data["block_roles"] = block_roles
        return self._call_api(
            "POST", f"/bitable/v1/apps/{app_token}/roles", data=data
        )

    def update_role(self, app_token, role_id, role_name, table_roles=None,
                    block_roles=None):
        """Update role permissions (full replace)."""
        data = {"role_name": role_name}
        if table_roles:
            data["table_roles"] = table_roles
        if block_roles:
            data["block_roles"] = block_roles
        return self._call_api(
            "PUT", f"/bitable/v1/apps/{app_token}/roles/{role_id}", data=data
        )

    def delete_role(self, app_token, role_id):
        """Delete custom role."""
        return self._call_api(
            "DELETE", f"/bitable/v1/apps/{app_token}/roles/{role_id}"
        )


class LarkRoleMemberClient(LarkAPIBase):
    """Collaborator management within roles. Max 200 collaborators per Base."""

    def list_role_members(self, app_token, role_id, page_size=100):
        """List collaborators in a role."""
        data = self._call_api(
            "GET", f"/bitable/v1/apps/{app_token}/roles/{role_id}/members",
            params={"page_size": page_size}
        )
        return data.get("items", data.get("members", []))

    def add_role_member(self, app_token, role_id, member_id,
                        member_type="open_id"):
        """Add single member to role. member_type: open_id, union_id, user_id."""
        return self._call_api(
            "POST",
            f"/bitable/v1/apps/{app_token}/roles/{role_id}/members",
            data={"member_id": member_id},
            params={"member_id_type": member_type}
        )

    def delete_role_member(self, app_token, role_id, member_id):
        """Remove member from role."""
        return self._call_api(
            "DELETE",
            f"/bitable/v1/apps/{app_token}/roles/{role_id}/members/{member_id}"
        )

    def batch_add_role_members(self, app_token, role_id, member_list):
        """Batch add members (max 1000).
        member_list: [{"member_id": ..., "member_type": "open_id"}]."""
        return self._call_api(
            "POST",
            f"/bitable/v1/apps/{app_token}/roles/{role_id}/members/batch_create",
            data={"member_list": member_list}
        )

    def batch_delete_role_members(self, app_token, role_id, member_ids):
        """Batch remove members (max 1000)."""
        return self._call_api(
            "POST",
            f"/bitable/v1/apps/{app_token}/roles/{role_id}/members/batch_delete",
            data={"member_ids": member_ids}
        )
