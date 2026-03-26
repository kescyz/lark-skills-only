"""
Lark Wiki Node API — 6 methods: create, get, list, move, copy, update_title.
Extends LarkAPIBase (curl-based HTTP, retry, pagination).

CRITICAL: get_node uses query param ?token= NOT path param.
Same URL for create (POST) and list (GET) nodes.
"""

from typing import Optional, Dict, Any
from lark_api_base import LarkAPIBase


class LarkWikiNodeClient(LarkAPIBase):
    """Node-level operations: create, get, list, move, copy, update_title."""

    def create_node(
        self,
        space_id: str,
        obj_type: str,
        parent_node_token: Optional[str] = None,
        title: Optional[str] = None,
        node_type: str = "origin"
    ) -> Dict[str, Any]:
        """
        Create a new node (page) in a Wiki space.

        Args:
            space_id: Target space identifier.
            obj_type: Document type — "doc", "docx", "sheet", "bitable", etc.
            parent_node_token: Parent node token. None = root level.
            title: Node title. Defaults to empty string if omitted.
            node_type: "origin" (real) or "shortcut" (alias). Default: "origin".

        Returns: {node} dict with node_token, obj_token, title, obj_type, etc.
        """
        body: Dict[str, Any] = {
            "obj_type": obj_type,
            "node_type": node_type,
        }
        if parent_node_token:
            body["parent_node_token"] = parent_node_token
        if title is not None:
            body["title"] = title

        data = self._call_api("POST", f"/wiki/v2/spaces/{space_id}/nodes", data=body)
        return data.get("node") or {}

    def get_node(self, token: str) -> Dict[str, Any]:
        """
        Get node metadata by its token.

        CRITICAL: Uses query param ?token= — NOT a path param.
        Endpoint: GET /wiki/v2/spaces/get_node?token=...

        Returns: {node} with node_token, obj_token, title, obj_type, parent_node_token, etc.
        """
        data = self._call_api("GET", "/wiki/v2/spaces/get_node", params={"token": token})
        return data.get("node") or {}

    def list_nodes(
        self,
        space_id: str,
        parent_node_token: Optional[str] = None,
        page_size: int = 50,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List nodes (children) in a space, optionally under a parent node.

        Same URL as create_node but GET method.
        Max page_size: 50. items can be null — returns [] if empty.

        Returns: {items, has_more, page_token}
        """
        params: Dict[str, Any] = {"page_size": min(page_size, 50)}
        if parent_node_token:
            params["parent_node_token"] = parent_node_token
        if page_token:
            params["page_token"] = page_token

        data = self._call_api("GET", f"/wiki/v2/spaces/{space_id}/nodes", params=params)
        return {
            "items": data.get("items") or [],
            "has_more": data.get("has_more", False),
            "page_token": data.get("page_token"),
        }

    def move_node(
        self,
        space_id: str,
        node_token: str,
        target_parent_token: Optional[str] = None,
        target_space_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Move a node to a new parent or different space.

        Cross-space moves supported via target_space_id.
        target_parent_token=None moves node to root of target space.

        Returns: {node} with updated location info.
        """
        body: Dict[str, Any] = {}
        if target_parent_token:
            body["target_parent_token"] = target_parent_token
        if target_space_id:
            body["target_space_id"] = target_space_id

        data = self._call_api(
            "POST",
            f"/wiki/v2/spaces/{space_id}/nodes/{node_token}/move",
            data=body
        )
        return data.get("node") or {}

    def copy_node(
        self,
        space_id: str,
        node_token: str,
        target_parent_token: Optional[str] = None,
        target_space_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Copy a node to a new location.

        Cross-space copies supported via target_space_id.
        title=None keeps the original title.

        Returns: {node} dict for the newly created copy.
        """
        body: Dict[str, Any] = {}
        if target_parent_token:
            body["target_parent_token"] = target_parent_token
        if target_space_id:
            body["target_space_id"] = target_space_id
        if title is not None:
            body["title"] = title

        data = self._call_api(
            "POST",
            f"/wiki/v2/spaces/{space_id}/nodes/{node_token}/copy",
            data=body
        )
        return data.get("node") or {}

    def update_title(
        self,
        space_id: str,
        node_token: str,
        title: str
    ) -> Dict[str, Any]:
        """
        Update the title of a Wiki node.

        LIMITATION: Only works for doc, docx, and shortcut node types.
        Does NOT work for: sheet, bitable, mindnote, file.

        Returns: {} on success (API returns empty data on success).
        """
        body = {"title": title}
        return self._call_api(
            "POST",
            f"/wiki/v2/spaces/{space_id}/nodes/{node_token}/update_title",
            data=body
        )
