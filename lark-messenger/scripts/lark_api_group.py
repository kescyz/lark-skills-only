"""Lark Messenger group management mixin — member listing, membership checks, chat updates."""

from typing import Dict, List

from lark_api_base import LarkAPIBase


class LarkGroupMixin(LarkAPIBase):
    """Group management methods: list members, check membership, update/delete chat."""

    def list_chat_members(self, chat_id: str,
                          member_id_type: str = "open_id") -> List[Dict]:
        """List all members in a group. Supports both tenant and user tokens.

        Note: bot is NOT included in results per API design.
        """
        return self._fetch_all(
            f"/im/v1/chats/{chat_id}/members",
            params={"member_id_type": member_id_type}
        )

    def is_in_chat(self, chat_id: str) -> bool:
        """Check if current bot/user (based on token) is in the group.

        Returns True/False from data.is_in_chat field.
        """
        data = self._call_api("GET", f"/im/v1/chats/{chat_id}/members/is_in_chat")
        return data.get("is_in_chat", False)

    def update_chat(self, chat_id: str, **kwargs) -> Dict:
        """Update group info. Tenant token only.

        kwargs: name, description, avatar (image_key), owner_id, etc.
        Returns updated chat data dict.
        """
        return self._call_api("PUT", f"/im/v1/chats/{chat_id}", data=kwargs)

    def delete_chat(self, chat_id: str) -> bool:
        """Delete/disband a group chat. Supports tenant and user tokens.

        Bot must be group owner or admin to disband.
        Returns True on success.
        """
        self._call_api("DELETE", f"/im/v1/chats/{chat_id}")
        return True
