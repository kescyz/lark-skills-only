"""
Lark Comment API client. Works on doc/docx/sheet/file types.

Content element structure (used in add_comment and add_reply):
  elements = [{"type": "text_run", "text_run": {"text": "..."}}]

All methods require file_type: doc | docx | sheet | file
"""
from typing import Dict, Any, List, Optional
from lark_api_base import LarkAPIBase


def _build_text_elements(content: str) -> List[Dict[str, Any]]:
    """Wrap plain text string into Lark reply_element array."""
    return [{"type": "text_run", "text_run": {"text": content}}]


class LarkCommentClient(LarkAPIBase):
    """Client for Lark Drive Comment APIs.

    Supported file_type values: doc, docx, sheet, file
    """

    def add_comment(
        self,
        file_token: str,
        file_type: str,
        content: str,
        quote_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a global comment to a file.

        Args:
            file_token: Document token (e.g. doccnGp4UK1UskrOEJwBXd3****)
            file_type: doc | docx | sheet | file
            content: Plain text comment content
            quote_content: Optional quoted text from document (for inline reference)

        Returns:
            Comment dict with comment_id, user_id, create_time, is_solved, reply_list, etc.
        """
        body = {
            "reply_list": {
                "replies": [
                    {
                        "content": {
                            "elements": _build_text_elements(content)
                        }
                    }
                ]
            }
        }

        return self._call_api(
            "POST",
            f"/drive/v1/files/{file_token}/comments",
            data=body,
            params={"file_type": file_type},
        )

    def list_comments(
        self,
        file_token: str,
        file_type: str,
        is_whole: Optional[bool] = None,
        is_solved: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """List all comments on a file (paginated, returns all).

        Args:
            file_token: Document token
            file_type: doc | docx | sheet | file
            is_whole: Filter — True for global comments only
            is_solved: Filter — True for solved, False for open

        Returns:
            List of comment dicts with comment_id, is_solved, is_whole, reply_list, etc.
        """
        params: Dict[str, Any] = {"file_type": file_type}
        if is_whole is not None:
            params["is_whole"] = str(is_whole).lower()
        if is_solved is not None:
            params["is_solved"] = str(is_solved).lower()

        return self._fetch_all(
            f"/drive/v1/files/{file_token}/comments",
            params=params,
        )

    def add_reply(
        self,
        file_token: str,
        file_type: str,
        comment_id: str,
        content: str,
    ) -> Dict[str, Any]:
        """Add a reply to an existing comment thread.

        Uses POST /drive/v1/files/:file_token/comments/:comment_id/replies
        with the same content element structure as add_comment.

        Args:
            file_token: Document token
            file_type: doc | docx | sheet | file
            comment_id: ID of the comment thread to reply to
            content: Plain text reply content

        Returns:
            Reply dict with reply_id, user_id, create_time, content, etc.
        """
        body = {
            "content": {
                "elements": _build_text_elements(content)
            }
        }

        return self._call_api(
            "POST",
            f"/drive/v1/files/{file_token}/comments/{comment_id}/replies",
            data=body,
            params={"file_type": file_type},
        )

    def solve_comment(
        self,
        file_token: str,
        file_type: str,
        comment_id: str,
        is_solved: bool = True,
    ) -> bool:
        """Mark a comment as resolved or restore it.

        Args:
            file_token: Document token
            file_type: doc | docx | sheet | file
            comment_id: ID of the comment to update
            is_solved: True to resolve, False to restore/reopen

        Returns:
            True on success (API returns empty data on success).
        """
        self._call_api(
            "PATCH",
            f"/drive/v1/files/{file_token}/comments/{comment_id}",
            data={"is_solved": is_solved},
            params={"file_type": file_type},
        )
        return True
