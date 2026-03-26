"""Lark Drive search and permission management — search files, add/update/delete members."""

from typing import Optional, List, Dict, Any
from lark_api_base import LarkAPIBase


class LarkDrivePermissionClient(LarkAPIBase):
    """Search files (user_token only) and manage file-level member permissions.

    Permission token: the file/doc token (same as file_token for most types).
    search_files: requires user_access_token — tenant_access_token not supported.
    """

    def search_files(
        self,
        query: str,
        docs_types: Optional[List[str]] = None,
        count: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search user-accessible documents by keyword.

        Uses /suite/docs-api/search/object (different path from drive/v1).
        Requires user_access_token — tenant token returns empty results.
        Results are permission-filtered (user sees only their accessible docs).

        Args:
            query: Search keyword (title + content keywords).
            docs_types: Filter by type — doc, sheet, slide, bitable, mindnote, file.
            count: Results per page (max 50).
            offset: Pagination offset (offset + count must be < 200).

        Returns:
            {docs_entities: [{token, type, title, owner_id}], total: int, has_more: bool}
        """
        data: Dict[str, Any] = {
            "search_key": query,
            "count": min(count, 50),
            "offset": offset,
        }
        if docs_types:
            data["docs_types"] = docs_types
        return self._call_api("POST", "/suite/docs-api/search/object", data=data)

    def add_permission(
        self,
        token: str,
        file_type: str,
        member_type: str,
        member_id: str,
        perm: str,
        need_notification: bool = False
    ) -> Dict[str, Any]:
        """Grant a user or group access to a file.

        Args:
            token: File/doc token (permission token).
            file_type: doc, sheet, file, wiki, bitable, docx.
            member_type: email, openid, openchat, opendepartmentid, userid.
            member_id: User/group identifier matching member_type.
            perm: view, edit, or full_access.
            need_notification: Send email notification (user_access_token only).

        Returns:
            {member: {member_type, member_id, perm, ...}}
        """
        data: Dict[str, Any] = {
            "member_type": member_type,
            "member_id": member_id,
            "perm": perm,
        }
        if need_notification:
            data["need_notification"] = True
        return self._call_api(
            "POST", f"/drive/v1/permissions/{token}/members",
            data=data,
            params={"type": file_type}
        )

    def update_permission(
        self,
        token: str,
        file_type: str,
        member_id: str,
        perm: str,
        member_type: str
    ) -> Dict[str, Any]:
        """Update an existing collaborator's permission level (full replace).

        Args:
            token: File/doc token.
            file_type: doc, sheet, file, wiki, bitable, docx.
            member_id: User/group identifier.
            perm: New permission — view, edit, or full_access.
            member_type: email, openid, openchat, opendepartmentid, userid.

        Returns:
            {member: {member_type, member_id, perm}}
        """
        return self._call_api(
            "PUT", f"/drive/v1/permissions/{token}/members/{member_id}",
            data={"perm": perm, "member_type": member_type},
            params={"type": file_type}
        )

    def delete_permission(
        self,
        token: str,
        file_type: str,
        member_id: str,
        member_type: str
    ) -> Dict[str, Any]:
        """Revoke a collaborator's access to a file.

        Args:
            token: File/doc token.
            file_type: doc, sheet, file, wiki, bitable, docx.
            member_id: User/group identifier to revoke.
            member_type: email, openid, openchat, opendepartmentid, userid.

        Returns:
            {} on success.
        """
        return self._call_api(
            "DELETE", f"/drive/v1/permissions/{token}/members/{member_id}",
            params={"type": file_type, "member_type": member_type}
        )
