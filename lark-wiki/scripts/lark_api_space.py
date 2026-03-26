"""
Lark Wiki Space API — 4 methods: list, get, create, update_setting.
Extends LarkAPIBase (curl-based HTTP, retry, pagination).
"""

from typing import Optional, Dict, Any
from lark_api_base import LarkAPIBase


class LarkWikiSpaceClient(LarkAPIBase):
    """Space-level operations: list, get, create, update settings."""

    def list_spaces(
        self,
        page_size: int = 50,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all Wiki spaces accessible to the token.

        Returns paginated result: {items, has_more, page_token}.
        Max page_size: 50. Supports both user and tenant access token.
        """
        params: Dict[str, Any] = {"page_size": min(page_size, 50)}
        if page_token:
            params["page_token"] = page_token

        data = self._call_api("GET", "/wiki/v2/spaces", params=params)
        return {
            "items": data.get("items") or [],
            "has_more": data.get("has_more", False),
            "page_token": data.get("page_token"),
        }

    def get_space(self, space_id: str) -> Dict[str, Any]:
        """
        Get Wiki space metadata by space_id.

        Returns: {space_id, name, description, space_type, visibility, ...}
        """
        data = self._call_api("GET", f"/wiki/v2/spaces/{space_id}")
        return data.get("space") or {}

    def create_space(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Wiki space.

        IMPORTANT: Requires user_access_token (not tenant_access_token).
        Returns: {space} with space_id, name, description.
        """
        body: Dict[str, Any] = {}
        if name:
            body["name"] = name
        if description:
            body["description"] = description

        data = self._call_api("POST", "/wiki/v2/spaces", data=body)
        return data.get("space") or {}

    def update_space_setting(
        self,
        space_id: str,
        create_setting: Optional[str] = None,
        security_setting: Optional[str] = None,
        comment_setting: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update Wiki space settings (admin only).

        Args:
            space_id: Target space identifier.
            create_setting: Who can create pages — "allow" or "not_allow".
            security_setting: External share — "allow" or "not_allow".
            comment_setting: Comments — "allow" or "not_allow".

        Returns: {setting} dict with updated values.
        """
        body: Dict[str, Any] = {}
        if create_setting is not None:
            body["create_setting"] = create_setting
        if security_setting is not None:
            body["security_setting"] = security_setting
        if comment_setting is not None:
            body["comment_setting"] = comment_setting

        data = self._call_api("PUT", f"/wiki/v2/spaces/{space_id}/setting", data=body)
        return data.get("setting") or {}
