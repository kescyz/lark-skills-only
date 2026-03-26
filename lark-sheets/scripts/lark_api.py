"""
Lark Sheets API client.
Mixed v2/v3 surface: v3 for spreadsheet/sheet management, v2 for data operations.
Styling, conditional formatting, and filter views live in lark_api_styling.py mixin.
"""

from lark_api_base import LarkAPIBase
from lark_api_styling import LarkSheetsStyleMixin
from typing import Dict, Any, List, Optional


class LarkSheetsClient(LarkSheetsStyleMixin, LarkAPIBase):
    """Spreadsheet operations via Lark Sheets API (v2 + v3).

    Domains:
        Spreadsheet (3): create_spreadsheet, get_spreadsheet, update_spreadsheet_properties
        Metadata (1):    get_metadata
        Sheets (3):      query_sheets, get_sheet, operate_sheets
        Data (5):        read_range, batch_read_ranges, write_range, batch_write_ranges, append_data
        Cells (3):       find_cells, merge_cells, unmerge_cells
        Dimensions (2):  insert_dimension, delete_dimension
        Styling (2):     format_cells, batch_format_cells  [mixin]
        Cond. Format (1):set_conditional_format             [mixin]
        Filter Views (3):create_filter_view, list_filter_views, delete_filter_view  [mixin]
    """

    # --- Spreadsheet Management (v3) ---

    def create_spreadsheet(self, title: str, folder_token: str = None) -> Dict[str, Any]:
        """Create new spreadsheet. Returns {spreadsheet: {spreadsheet_token, title, url}}."""
        body: Dict[str, Any] = {"title": title}
        if folder_token:
            body["folder_token"] = folder_token
        return self._call_api("POST", "/sheets/v3/spreadsheets", data=body)

    def get_spreadsheet(self, spreadsheet_token: str) -> Dict[str, Any]:
        """Get spreadsheet info. Returns {spreadsheet: {title, url, owner_id}}."""
        return self._call_api("GET", f"/sheets/v3/spreadsheets/{spreadsheet_token}")

    def update_spreadsheet_properties(self, spreadsheet_token: str, title: str) -> Dict[str, Any]:
        """Update spreadsheet title."""
        return self._call_api("PATCH", f"/sheets/v3/spreadsheets/{spreadsheet_token}", data={"title": title})

    def get_metadata(self, spreadsheet_token: str) -> Dict[str, Any]:
        """Get full metadata including all sheets. Returns {spreadsheetToken, properties, sheets: [...]}."""
        return self._call_api("GET", f"/sheets/v2/spreadsheets/{spreadsheet_token}/metainfo")

    # --- Sheet Management (v3 + v2) ---

    def query_sheets(self, spreadsheet_token: str) -> List[Dict[str, Any]]:
        """List all sheets in spreadsheet. Returns list of {sheet_id, title, index}."""
        data = self._call_api("GET", f"/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query")
        return data.get("sheets") or []

    def get_sheet(self, spreadsheet_token: str, sheet_id: str) -> Dict[str, Any]:
        """Get single sheet properties."""
        return self._call_api("GET", f"/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/{sheet_id}")

    def operate_sheets(self, spreadsheet_token: str, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Batch sheet ops (add/copy/delete/update). Each request has one key: addSheet/copySheet/deleteSheet/updateSheet."""
        return self._call_api(
            "POST", f"/sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update",
            data={"requests": requests}
        )

    # --- Data Operations (v2) ---

    def read_range(self, spreadsheet_token: str, range: str,
                   value_render: str = None, date_time_render: str = None) -> Dict[str, Any]:
        """Read data from range (A1 notation: 'sheetId!A1:C3'). Returns {valueRange: {values: [[...]]}}."""
        params: Dict[str, Any] = {}
        if value_render:
            params["valueRenderOption"] = value_render
        if date_time_render:
            params["dateTimeRenderOption"] = date_time_render
        return self._call_api(
            "GET", f"/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range}",
            params=params or None
        )

    def batch_read_ranges(self, spreadsheet_token: str, ranges: List[str],
                          value_render: str = None, date_time_render: str = None) -> Dict[str, Any]:
        """Read data from multiple ranges. Returns {valueRanges: [...]}."""
        params: Dict[str, Any] = {"ranges": ",".join(ranges)}
        if value_render:
            params["valueRenderOption"] = value_render
        if date_time_render:
            params["dateTimeRenderOption"] = date_time_render
        return self._call_api(
            "GET", f"/sheets/v2/spreadsheets/{spreadsheet_token}/values_batch_get",
            params=params
        )

    def write_range(self, spreadsheet_token: str, range: str, values: List[List]) -> Dict[str, Any]:
        """Write 2D array to range. Returns {updatedRange, updatedRows, updatedColumns, updatedCells}."""
        return self._call_api(
            "PUT", f"/sheets/v2/spreadsheets/{spreadsheet_token}/values",
            data={"valueRange": {"range": range, "values": values}}
        )

    def batch_write_ranges(self, spreadsheet_token: str, value_ranges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Write to multiple ranges. Each item: {"range": "sheetId!A1:B2", "values": [[...]]}."""
        return self._call_api(
            "POST", f"/sheets/v2/spreadsheets/{spreadsheet_token}/values_batch_update",
            data={"valueRanges": value_ranges}
        )

    def append_data(self, spreadsheet_token: str, range: str, values: List[List],
                    insert_data_option: str = "OVERWRITE") -> Dict[str, Any]:
        """Append data after last row in range. insert_data_option: OVERWRITE or INSERT_ROWS."""
        return self._call_api(
            "POST", f"/sheets/v2/spreadsheets/{spreadsheet_token}/values_append",
            data={"valueRange": {"range": range, "values": values}},
            params={"insertDataOption": insert_data_option}
        )

    # --- Cell Operations (v3 + v2) ---

    def find_cells(self, spreadsheet_token: str, sheet_id: str,
                   find: str, find_condition: Dict[str, Any] = None) -> Dict[str, Any]:
        """Find cells matching string. Returns {find_result: {matched_cells: [...]}}."""
        body: Dict[str, Any] = {"find": find}
        if find_condition:
            body["find_condition"] = find_condition
        return self._call_api(
            "POST", f"/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/{sheet_id}/find",
            data=body
        )

    def merge_cells(self, spreadsheet_token: str, range: str,
                    merge_type: str = "MERGE_ALL") -> Dict[str, Any]:
        """Merge cells in range. merge_type: MERGE_ALL, MERGE_ROWS, MERGE_COLUMNS."""
        return self._call_api(
            "POST", f"/sheets/v2/spreadsheets/{spreadsheet_token}/merge_cells",
            data={"range": range, "mergeType": merge_type}
        )

    def unmerge_cells(self, spreadsheet_token: str, range: str) -> Dict[str, Any]:
        """Unmerge previously merged cells."""
        return self._call_api(
            "POST", f"/sheets/v2/spreadsheets/{spreadsheet_token}/unmerge_cells",
            data={"range": range}
        )

    # --- Dimension Operations (v2) ---

    def insert_dimension(self, spreadsheet_token: str, sheet_id: str,
                         major_dimension: str, start_index: int,
                         end_index: int, inherit_style: str = "BEFORE") -> Dict[str, Any]:
        """Insert rows/columns. major_dimension: ROWS/COLUMNS, indices 0-based, inherit_style: BEFORE/AFTER."""
        return self._call_api(
            "POST", f"/sheets/v2/spreadsheets/{spreadsheet_token}/insert_dimension_range",
            data={
                "dimension": {
                    "sheetId": sheet_id,
                    "majorDimension": major_dimension,
                    "startIndex": start_index,
                    "endIndex": end_index,
                },
                "inheritStyle": inherit_style,
            }
        )

    def delete_dimension(self, spreadsheet_token: str, sheet_id: str,
                         major_dimension: str, start_index: int,
                         end_index: int) -> Dict[str, Any]:
        """Delete rows/columns. Max 5000 per request. major_dimension: ROWS/COLUMNS, indices 0-based."""
        return self._call_api(
            "DELETE", f"/sheets/v2/spreadsheets/{spreadsheet_token}/dimension_range",
            data={
                "dimension": {
                    "sheetId": sheet_id,
                    "majorDimension": major_dimension,
                    "startIndex": start_index,
                    "endIndex": end_index,
                }
            }
        )
