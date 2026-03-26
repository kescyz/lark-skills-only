"""
Lark Wiki Member API — 5 methods: add_member, delete_member, search_wiki,
move_docs_to_wiki, get_task.
Extends LarkAPIBase (curl-based HTTP, retry, pagination).

CRITICAL: delete_member requires body params despite being a DELETE request.
search_wiki and create_space require user_access_token only.
move_docs_to_wiki is async: returns wiki_token (immediate) OR task_id (pending).
"""

from typing import Optional, Dict, Any
from lark_api_base import LarkAPIBase


class LarkWikiMemberClient(LarkAPIBase):
    """Member management, search, doc migration, and async task polling."""

    def add_member(
        self,
        space_id: str,
        member_type: str,
        member_id: str,
        member_role: str,
        need_notification: bool = False
    ) -> Dict[str, Any]:
        """
        Add a member to a Wiki space.

        Args:
            space_id: Target space identifier.
            member_type: "userid", "openid", "unionid", "email",
                         "departmentid", "openchatid".
            member_id: ID of the member corresponding to member_type.
            member_role: "admin" or "member".
            need_notification: Send notification to added member. Default False.

        Notes:
            - Public space: can only add/remove admins (error 131101 for member role).
            - Personal space: can only add/remove members (error 131101 for admin role).

        Returns: {member} dict with member_id, member_type, member_role.
        """
        body: Dict[str, Any] = {
            "member_type": member_type,
            "member_id": member_id,
            "member_role": member_role,
            "need_notification": need_notification,
        }
        data = self._call_api("POST", f"/wiki/v2/spaces/{space_id}/members", data=body)
        return data.get("member") or {}

    def delete_member(
        self,
        space_id: str,
        member_id: str,
        member_type: str,
        member_role: str
    ) -> Dict[str, Any]:
        """
        Remove a member from a Wiki space.

        CRITICAL: This DELETE request requires a JSON body — member_type and
        member_role must be sent as body params (not query params).

        Args:
            space_id: Target space identifier.
            member_id: ID of the member to remove.
            member_type: "userid", "openid", "unionid", etc.
            member_role: "admin" or "member".

        Returns: {} on success.
        """
        body: Dict[str, Any] = {
            "member_type": member_type,
            "member_role": member_role,
        }
        return self._call_api(
            "DELETE",
            f"/wiki/v2/spaces/{space_id}/members/{member_id}",
            data=body
        )

    def search_wiki(
        self,
        query: str,
        space_id: Optional[str] = None,
        node_id: Optional[str] = None,
        page_size: int = 20,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full-text search across Wiki nodes.

        IMPORTANT: Requires user_access_token (not tenant_access_token).

        Args:
            query: Search keyword string.
            space_id: Limit search to specific space. None = all spaces.
            node_id: Limit search to subtree under node. None = entire space.
            page_size: Results per page (max 50). Default 20.
            page_token: Pagination token from previous call.

        Returns: {items, has_more, page_token} — items are node search results.
        """
        body: Dict[str, Any] = {
            "query": query,
            "page_size": min(page_size, 50),
        }
        if space_id:
            body["space_id"] = space_id
        if node_id:
            body["node_id"] = node_id
        if page_token:
            body["page_token"] = page_token

        data = self._call_api("POST", "/wiki/v2/nodes/search", data=body)
        return {
            "items": data.get("items") or [],
            "has_more": data.get("has_more", False),
            "page_token": data.get("page_token"),
        }

    def move_docs_to_wiki(
        self,
        space_id: str,
        obj_type: str,
        obj_token: str,
        parent_wiki_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Move an existing Lark document into a Wiki space (async operation).

        After calling, check the response:
        - If "wiki_token" present: move completed immediately.
        - If "task_id" present: move is async, poll with get_task(task_id).

        Args:
            space_id: Target Wiki space identifier.
            obj_type: Document type — "doc", "docx", "sheet", "bitable", "mindnote", "file".
            obj_token: Token of the document to move.
            parent_wiki_token: Parent node token in Wiki. None = root.

        Returns: {wiki_token?, task_id?} — one or both fields present.
        """
        body: Dict[str, Any] = {
            "obj_type": obj_type,
            "obj_token": obj_token,
        }
        if parent_wiki_token:
            body["parent_wiki_token"] = parent_wiki_token

        return self._call_api(
            "POST",
            f"/wiki/v2/spaces/{space_id}/nodes/move_docs_to_wiki",
            data=body
        )

    def get_task(self, task_id: str, task_type: str = "move") -> Dict[str, Any]:
        """
        Poll status of an async Wiki task (e.g., move_docs_to_wiki).

        Only the task creator can query task status.

        Args:
            task_id: Task identifier returned by move_docs_to_wiki.
            task_type: Task category. Currently only "move" is supported.

        Returns: {task} with status ("pending", "done", "failed") and result info.
        """
        params = {"task_type": task_type}
        data = self._call_api("GET", f"/wiki/v2/tasks/{task_id}", params=params)
        return data.get("task") or {}
