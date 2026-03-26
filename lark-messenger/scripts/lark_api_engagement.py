"""Lark Messenger engagement mixin — message forwarding, reactions, pins, batch send."""

from typing import Dict, List, Optional

from lark_api_base import LarkAPIBase


class LarkEngagementMixin(LarkAPIBase):
    """Message engagement: forward, react, pin, batch send."""

    def forward_message(self, message_id: str, receive_id: str,
                        receive_id_type: str = "chat_id") -> Dict:
        """Forward a single message to a user or group. Tenant token only.

        receive_id_type: chat_id | open_id | user_id | union_id | email | thread_id
        """
        return self._call_api(
            "POST", f"/im/v1/messages/{message_id}/forward",
            data={"receive_id": receive_id},
            params={"receive_id_type": receive_id_type}
        )

    def add_reaction(self, message_id: str, emoji_type: str) -> Dict:
        """Add an emoji reaction to a message. Supports both tenant and user tokens.

        emoji_type: e.g. "SMILE", "THUMBSUP" — see Lark emoji introduction doc.
        Returns reaction data including reaction_id.
        """
        return self._call_api(
            "POST", f"/im/v1/messages/{message_id}/reactions",
            data={"reaction_type": {"emoji_type": emoji_type}}
        )

    def list_reactions(self, message_id: str,
                       reaction_type: str = None) -> List[Dict]:
        """List all reactions on a message. Supports both tenant and user tokens.

        reaction_type: optional filter by emoji type (e.g. "SMILE"). If omitted, returns all.
        """
        params = {}
        if reaction_type:
            params["reaction_type"] = reaction_type
        return self._fetch_all(
            f"/im/v1/messages/{message_id}/reactions",
            params=params
        )

    def pin_message(self, message_id: str) -> Dict:
        """Pin a message in its group chat. Tenant token only.

        Bot must be in the group. Returns pin data including chat_id and create_time.
        If already pinned, returns the existing pin info.
        """
        return self._call_api(
            "POST", "/im/v1/pins",
            data={"message_id": message_id}
        )

    def batch_send(self, msg_type: str, content: str,
                   dept_ids: Optional[List[str]] = None,
                   open_ids: Optional[List[str]] = None) -> Dict:
        """Send message to multiple users or departments. Tenant token only.

        Async API — 500k messages/day limit. Cannot update or reply to batch messages.
        content: JSON string (text) or dict (card) per msg_type format.
        dept_ids: list of custom department IDs (max 200).
        open_ids: list of user open_ids (max 200).
        At least one of dept_ids or open_ids must be provided.
        """
        body: Dict = {"msg_type": msg_type}
        if isinstance(content, str):
            # text/post/image/share_chat: wrap in content field
            body["content"] = content
        else:
            # interactive card: use card field
            body["card"] = content
        body["department_ids"] = dept_ids or []
        body["open_ids"] = open_ids or []
        return self._call_api("POST", "/message/v4/batch_send/", data=body)
