# Lark Sheets API Reference

> Token management handled by `lark-token-manager` MCP server.
> See [api-examples.md](./api-examples.md) for code samples.
> See [api-validation.md](./api-validation.md) for enums, limits, error codes.

```python
from lark_api import LarkSheetsClient
client = LarkSheetsClient(access_token="u-xxx", user_open_id="ou_xxx")
```

API surface: v3 for spreadsheet/sheet management, v2 for data operations.

---

## Spreadsheet Management

| Method | Key Params | Returns |
|--------|-----------|---------|
| `create_spreadsheet(title, folder_token=None)` | `title` (req), `folder_token` (opt) | `{spreadsheet: {spreadsheet_token, title, url}}` |
| `get_spreadsheet(spreadsheet_token)` | `spreadsheet_token` (req) | `{spreadsheet: {spreadsheet_token, title, url, owner_id}}` |
| `update_spreadsheet_properties(spreadsheet_token, title)` | both req | `{}` |
| `get_metadata(spreadsheet_token)` | `spreadsheet_token` (req) | `{spreadsheetToken, properties, sheets: [{sheetId, title, index, rowCount, columnCount}]}` |

---

## Sheet Management

| Method | Key Params | Returns |
|--------|-----------|---------|
| `query_sheets(spreadsheet_token)` | `spreadsheet_token` (req) | `[{sheet_id, title, index}]` |
| `get_sheet(spreadsheet_token, sheet_id)` | both req | `{sheet: {sheet_id, title, index, grid_properties}}` |
| `operate_sheets(spreadsheet_token, requests)` | `requests`: list of op dicts (one key each) | `{replies: [...]}` |

**operate_sheets request shapes**:
```python
{"addSheet":    {"properties": {"title": "Sheet2", "index": 1}}}
{"copySheet":   {"source": sheet_id, "destination": {"title": "Copy"}}}
{"deleteSheet": {"sheetId": sheet_id}}
{"updateSheet": {"properties": {"sheetId": sheet_id, "title": "New Name"}}}
```

---

## Data Operations

### read_range(spreadsheet_token, range, value_render=None, date_time_render=None)

| Param | Type | Req | Notes |
|-------|------|-----|-------|
| spreadsheet_token | string | Yes | — |
| range | string | Yes | A1 format: `sheetId!A1:C3` |
| value_render | string | No | ToString \| FormattedValue \| Formula \| UnformattedValue |
| date_time_render | string | No | FormattedString |

**Returns**: `{valueRange: {range, values: [[cell, ...]]}}`

---

### batch_read_ranges(spreadsheet_token, ranges, value_render=None, date_time_render=None)

Same render options as `read_range`. `ranges` is `list[string]`.

**Returns**: `{valueRanges: [{range, values: [[...]]}]}`

---

### write_range(spreadsheet_token, range, values)

`values`: 2D list. Max 5000 rows, 100 cols per call.

**Returns**: `{updatedRange, updatedRows, updatedColumns, updatedCells}`

---

### batch_write_ranges(spreadsheet_token, value_ranges)

`value_ranges`: `[{"range": "sheetId!A1:B2", "values": [[...]]}]`

**Returns**: `{responses: [{updatedRange, updatedCells}]}`

---

### append_data(spreadsheet_token, range, values, insert_data_option="OVERWRITE")

| Param | Values |
|-------|--------|
| insert_data_option | `OVERWRITE` (default) — write from last row; `INSERT_ROWS` — push existing data down |

**Returns**: `{updates: {updatedRange, updatedRows, updatedColumns, updatedCells}}`

---

## Cell Operations

### find_cells(spreadsheet_token, sheet_id, find, condition=None)

`condition` (optional dict):
```python
{"match_case": bool, "match_entire_cell": bool, "regex": bool}
```

**Returns**: `{find_result: {matched_cells: [{row, col}]}}`

---

### merge_cells(spreadsheet_token, range, merge_type="MERGE_ALL")

| merge_type | Behavior |
|-----------|---------|
| `MERGE_ALL` | Merge entire selection into one cell |
| `MERGE_ROWS` | Merge within each row independently |
| `MERGE_COLUMNS` | Merge within each column independently |

---

### unmerge_cells(spreadsheet_token, range)

Range must exactly match an existing merged region. **Returns**: `{}`

---

## Dimension Operations

### insert_dimension(spreadsheet_token, sheet_id, major_dimension, start_index, end_index, inherit_style="BEFORE")

| Param | Type | Req | Notes |
|-------|------|-----|-------|
| major_dimension | string | Yes | `ROWS` or `COLUMNS` |
| start_index | int | Yes | 0-based |
| end_index | int | Yes | 0-based, exclusive |
| inherit_style | string | No | `BEFORE` (default) or `AFTER` |

---

### delete_dimension(spreadsheet_token, sheet_id, major_dimension, start_index, end_index)

Same index rules as insert. Max span: 5000 rows/columns. **Returns**: `{}`

---

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 99991663 | Token expired | MCP `refresh_lark_token` |
| 99991664 | Permission denied | Check `sheets:spreadsheet` scope |
| 1254290 | Rate limited | Backoff 2s → 4s → 8s |
| 190002 | Invalid parameters | Check field names/types |
| 190003 | Internal error | Retry; escalate if persistent |
