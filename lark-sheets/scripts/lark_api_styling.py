"""Lark Sheets styling, conditional formatting, and filter view operations."""

from typing import Dict, Any, List
from lark_api_base import LarkAPIBase


class LarkSheetsStyleMixin(LarkAPIBase):
    """Mixin for cell styling, conditional formatting, and filter views.

    All v2 style endpoints, v2 conditional format endpoints, v3 filter view endpoints.
    """

    # --- Cell Styling (v2) ---

    def format_cells(
        self,
        spreadsheet_token: str,
        range_str: str,
        style: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set cell formatting for a single range (font, fill, border, alignment).

        Args:
            spreadsheet_token: Spreadsheet token.
            range_str: A1-notation range, e.g. "sheetId!A1:C3".
            style: Style dict — keys: font, textDecoration, formatter, hAlign, vAlign,
                   foreColor, backColor, borderType, borderColor, clean.

        Returns:
            {spreadsheetToken, updatedRange, updatedRows, updatedColumns, updatedCells, revision}
        """
        return self._call_api(
            "PUT", f"/sheets/v2/spreadsheets/{spreadsheet_token}/style",
            data={"appendStyle": {"range": range_str, "style": style}}
        )

    def batch_format_cells(
        self,
        spreadsheet_token: str,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Set cell formatting for multiple ranges in one request.

        Args:
            spreadsheet_token: Spreadsheet token.
            data: List of {"ranges": [...], "style": {...}} objects (max 10 per request).

        Returns:
            {spreadsheetToken, totalUpdatedRows, totalUpdatedColumns, totalUpdatedCells,
             revision, responses: [...]}
        """
        return self._call_api(
            "PUT", f"/sheets/v2/spreadsheets/{spreadsheet_token}/styles_batch_update",
            data={"data": data}
        )

    # --- Conditional Formatting (v2) ---

    def set_conditional_format(
        self,
        spreadsheet_token: str,
        sheet_id: str,
        rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create conditional formatting rules (up to 10 at once).

        Args:
            spreadsheet_token: Spreadsheet token.
            sheet_id: Sheet ID.
            rules: List of condition_format dicts, each with:
                   ranges, rule_type (containsBlanks/notContainsBlanks/duplicateValues/
                   uniqueValues/cellIs/containsText/timePeriod), attrs, style.

        Returns:
            List of {sheet_id, cf_id, res_code, res_msg} per rule.
        """
        sheet_condition_formats = [
            {"sheet_id": sheet_id, "condition_format": rule}
            for rule in rules
        ]
        data = self._call_api(
            "POST",
            f"/sheets/v2/spreadsheets/{spreadsheet_token}/condition_formats/batch_create",
            data={"sheet_condition_formats": sheet_condition_formats}
        )
        return data.get("responses") or []

    # --- Filter Views (v3) ---

    def create_filter_view(
        self,
        spreadsheet_token: str,
        sheet_id: str,
        range_str: str,
        filter_name: str = None,
        filter_view_id: str = None
    ) -> Dict[str, Any]:
        """Create a saved filter view on a sheet. Max 150 per sheet.

        Args:
            spreadsheet_token: Spreadsheet token.
            sheet_id: Sheet ID.
            range_str: Filter range e.g. "sheetId!A1:H20".
            filter_name: Optional view name (max 100 chars; auto-generated if omitted).
            filter_view_id: Optional ID (10 chars; auto-generated if omitted).

        Returns:
            {filter_view_id, filter_view_name, range}
        """
        body: Dict[str, Any] = {"range": range_str}
        if filter_name:
            body["filter_view_name"] = filter_name
        if filter_view_id:
            body["filter_view_id"] = filter_view_id
        data = self._call_api(
            "POST",
            f"/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/{sheet_id}/filter_views",
            data=body
        )
        return data.get("filter_view") or {}

    def list_filter_views(
        self,
        spreadsheet_token: str,
        sheet_id: str
    ) -> List[Dict[str, Any]]:
        """List all filter views in a sheet.

        Returns:
            List of {filter_view_id, filter_view_name, range}.
        """
        data = self._call_api(
            "GET",
            f"/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/{sheet_id}/filter_views/query"
        )
        return data.get("items") or []

    def delete_filter_view(
        self,
        spreadsheet_token: str,
        sheet_id: str,
        filter_view_id: str
    ) -> bool:
        """Delete a filter view by ID.

        Returns:
            True on success (API returns empty data on success).
        """
        self._call_api(
            "DELETE",
            f"/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/{sheet_id}"
            f"/filter_views/{filter_view_id}"
        )
        return True
