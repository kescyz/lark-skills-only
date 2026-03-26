"""Lark Drive export task operations — create, poll, and check async export tasks."""

from typing import Dict, Any
from lark_api_base import LarkAPIBase


class LarkDriveExportClient(LarkAPIBase):
    """Async export workflow for Drive documents (doc/docx/sheet/bitable → pdf/docx/xlsx/csv).

    Usage (two-step async flow):
        ticket = client.export_file(file_token, file_type="sheet", export_type="xlsx")
        result = client.get_export_result(ticket, file_token)
        # Poll until result["job_status"] == 0, then download via result["file_token"]
    """

    def export_file(
        self,
        file_token: str,
        file_type: str,
        export_type: str = "pdf",
        sub_id: str = None
    ) -> str:
        """Start an async export task. Returns ticket for polling.

        Args:
            file_token: Token of the document to export.
            file_type: Source doc type — doc, docx, sheet, bitable.
            export_type: Output format — pdf, docx (doc/docx only),
                         xlsx or csv (sheet/bitable only).
            sub_id: Sheet/table ID, required only when exporting sheet/bitable to csv.

        Returns:
            ticket string — pass to get_export_result() to poll status.
        """
        body: Dict[str, Any] = {
            "file_extension": export_type,
            "token": file_token,
            "type": file_type,
        }
        if sub_id:
            body["sub_id"] = sub_id
        data = self._call_api("POST", "/drive/v1/export_tasks", data=body)
        return data.get("ticket", "")

    def get_export_result(self, ticket: str, file_token: str) -> Dict[str, Any]:
        """Poll export task status by ticket.

        Args:
            ticket: Export task ID returned by export_file().
            file_token: Same document token used when creating the task (required query param).

        Returns:
            {job_status, file_extension, type, file_name, file_token, file_size, job_error_msg}
            job_status: 0=success, 1=init, 2=processing, 3+=error (see API docs).
            On success, use file_token to download via download_file().
        """
        data = self._call_api(
            "GET", f"/drive/v1/export_tasks/{ticket}",
            params={"token": file_token}
        )
        return data.get("result") or {}
