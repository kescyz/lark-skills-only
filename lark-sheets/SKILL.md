---
name: lark-sheets
description: LarkSuite spreadsheet management - spreadsheets, sheets, data, excel ranges. Use when user asks about spreadsheets, sheets, excel data, table data, or ranges. Requires lark-token-manager MCP.
---

# Lark Sheets

Manage LarkSuite spreadsheets: create/read/write ranges, manage sheets, format cells, insert/delete rows and columns.

## Prerequisites

- `lark-token-manager` MCP server configured in `.mcp.json`
- Lark app with `sheets:spreadsheet` scope

## Initialization

### Step 1: Get user info from MCP

Call MCP `whoami` to get:
- `linked_users[].lark_open_id` -> user_open_id

### Step 2: Get access token from MCP

Call MCP `get_lark_token(app_name=LARK_APP_NAME)`
- If expired: MCP `refresh_lark_token` -> if fails: MCP `start_oauth`

### Step 3: Initialize client

```python
import sys, os

# Find scripts path relative to SKILL.md location
skill_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(skill_dir, 'scripts'))

from lark_api import LarkSheetsClient
from utils import make_range, col_to_letter, letter_to_col

client = LarkSheetsClient(
    access_token=TOKEN_FROM_MCP,
    user_open_id=OPEN_ID_FROM_WHOAMI
)
```

## Encoding (Non-ASCII Data)

ALWAYS use the Python scripts (`scripts/`) for ALL API calls. NEVER use `curl` in Bash for requests containing non-ASCII characters (Vietnamese, Chinese, Japanese, etc.). Windows terminal encoding (cp1252) corrupts UTF-8 data, causing mojibake. The Python scripts use `urllib.request` with proper `ensure_ascii=False` encoding - this is the correct and safe approach.

## API Methods

### Spreadsheet Management

| Method | Description |
|--------|-------------|
| `create_spreadsheet(title, folder_token=None)` | Create new spreadsheet in optional Drive folder. Returns `{spreadsheet: {spreadsheet_token, title, url}}`. Use `spreadsheet_token` for all subsequent calls. |
| `get_spreadsheet(spreadsheet_token)` | Get spreadsheet info including title, url, owner_id. Returns `{spreadsheet: {...}}`. |
| `update_spreadsheet_properties(spreadsheet_token, title)` | Rename spreadsheet. Only `title` is updatable. Returns updated spreadsheet properties. |
| `get_metadata(spreadsheet_token)` | Get full metadata including all sheets list with indices. Uses v2 endpoint. Returns `{spreadsheetToken, properties, sheets: [{sheetId, title, index, ...}]}`. |

### Sheet Management

| Method | Description |
|--------|-------------|
| `query_sheets(spreadsheet_token)` | List all sheets. Returns list of `{sheet_id, title, index}`. Use `sheet_id` (not title) for range notation. |
| `get_sheet(spreadsheet_token, sheet_id)` | Get single sheet properties including grid dimensions. Returns `{sheet: {sheet_id, title, index, ...}}`. |
| `operate_sheets(spreadsheet_token, requests)` | Batch sheet operations. Each request dict must have exactly one key: `addSheet`, `copySheet`, `deleteSheet`, or `updateSheet`. See api-reference.md for each request shape. |

### Data Operations

| Method | Description |
|--------|-------------|
| `read_range(spreadsheet_token, range, value_render=None, date_time_render=None)` | Read data from A1 range like `sheetId!A1:C3`. Returns `{valueRange: {values: [[...]]}}`. `value_render` controls how values are rendered (default: FormattedValue). |
| `batch_read_ranges(spreadsheet_token, ranges, value_render=None, date_time_render=None)` | Read multiple ranges in one call. Returns `{valueRanges: [...]}`. More efficient than multiple single reads. |
| `write_range(spreadsheet_token, range, values)` | Write 2D array to range. `values` is list of rows, each a list of cell values. Returns `{updatedRange, updatedRows, updatedColumns, updatedCells}`. |
| `batch_write_ranges(spreadsheet_token, value_ranges)` | Write to multiple ranges atomically. Each item: `{"range": "sheetId!A1:B2", "values": [[...]]}`. |
| `append_data(spreadsheet_token, range, values, insert_data_option="OVERWRITE")` | Append rows after last non-empty row in range. `INSERT_ROWS` shifts existing data down; `OVERWRITE` overwrites from last row. |

### Cell Operations

| Method | Description |
|--------|-------------|
| `find_cells(spreadsheet_token, sheet_id, find, condition=None)` | Find cells matching a string value. Returns `{find_result: {matched_cells: [{row, col}]}}`. `condition` can set `match_case`, `match_entire_cell`, `regex`. |
| `merge_cells(spreadsheet_token, range, merge_type="MERGE_ALL")` | Merge cells in range. `MERGE_ALL` merges entire selection; `MERGE_ROWS` merges within each row; `MERGE_COLUMNS` merges within each column. |
| `unmerge_cells(spreadsheet_token, range)` | Unmerge previously merged cells. Range must exactly match a merged region. |

### Dimension Operations

| Method | Description |
|--------|-------------|
| `insert_dimension(spreadsheet_token, sheet_id, major_dimension, start_index, end_index, inherit_style="BEFORE")` | Insert empty rows or columns. Indices are 0-based. `inherit_style` controls which neighbor's formatting to copy: `BEFORE` (row/col before) or `AFTER`. |
| `delete_dimension(spreadsheet_token, sheet_id, major_dimension, start_index, end_index)` | Delete rows or columns. Indices are 0-based. Max 5000 rows/columns per request. |

### Styling & Formatting

| Method | Description |
|--------|-------------|
| `format_cells(spreadsheet_token, range_str, style)` | Set cell formatting for a single range. `style` keys: `font`, `textDecoration`, `formatter`, `hAlign`, `vAlign`, `foreColor`, `backColor`, `borderType`, `borderColor`, `clean`. |
| `batch_format_cells(spreadsheet_token, data)` | Set formatting for multiple ranges in one request. `data`: list of `{"ranges": [...], "style": {...}}` (max 10). |
| `set_conditional_format(spreadsheet_token, sheet_id, rules)` | Create conditional formatting rules (up to 10). Each rule has `ranges`, `rule_type`, `attrs`, `style`. Returns list of results per rule. |

### Filter Views

| Method | Description |
|--------|-------------|
| `create_filter_view(spreadsheet_token, sheet_id, range_str, filter_name=None, filter_view_id=None)` | Create a saved filter view on a sheet. Max 150 per sheet. Returns `{filter_view_id, filter_view_name, range}`. |
| `list_filter_views(spreadsheet_token, sheet_id)` | List all filter views in a sheet. Returns list of `{filter_view_id, filter_view_name, range}`. |
| `delete_filter_view(spreadsheet_token, sheet_id, filter_view_id)` | Delete a filter view by ID. Returns `bool`. |

## Range Notation

> **Range Notation**: Uses A1 format — `{sheet_id}!A1:C3` or `{sheet_id}!A1`.
> Sheet ID is the `sheet_id` from `query_sheets()`, NOT the sheet title.
> Column letters: A-Z, AA-AZ, BA-BZ, etc. Row numbers: 1-based.
> Examples: `abc123!A1:D10`, `abc123!A:D` (full columns), `abc123!1:10` (full rows).

Use `make_range(sheet_id, "A1", "D10")` to build range strings safely.

## Quick Examples

### Create spreadsheet and write data
```python
# Create
result = client.create_spreadsheet("Báo cáo doanh thu Q1 2026")
token = result["spreadsheet"]["spreadsheet_token"]

# Get first sheet ID
sheets = client.query_sheets(token)
sheet_id = sheets[0]["sheet_id"]

# Write headers and data
rng = make_range(sheet_id, "A1", "C1")
client.write_range(token, rng, [["Nhân viên", "Doanh thu", "Khu vực"]])
client.append_data(token, make_range(sheet_id, "A1", "C1"), [
    ["Nguyễn Văn A", 50000000, "Hà Nội"],
    ["Trần Thị B", 75000000, "TP.HCM"],
])
```

### Read data back
```python
data = client.read_range(token, make_range(sheet_id, "A1", "C10"))
rows = data["valueRange"]["values"]
for row in rows:
    print(row)
```

## Personnel Lookup

Use MCP tools directly - no Python needed:

**Find specific people:**
```
search_users(query="Huong") -> [{name, email, department, lark_open_id, ...}]
```

**List department members:**
```
list_departments() -> [{department_id, name, ...}]
list_department_users(department_id) -> [{user_id, open_id, name, ...}]
```

Use `lark_open_id` with `member_type="openid"` for Drive permissions.

## Cross-Domain Operations

**Delete spreadsheet** (Drive API):
```
DELETE /open-apis/drive/v1/files/{spreadsheet_token}?type=sheet
```

**Share spreadsheet** (Drive Permissions API):
```
POST /open-apis/drive/v1/permissions/{spreadsheet_token}/members
Body: {"member_type": "openid", "member_id": "ou_xxx", "perm": "view"}
type param: ?type=sheet
```

## References

- [API Reference](./references/api-reference.md) — all methods with params (required/optional, types, return shapes)
- [Examples](./references/api-examples.md) — realistic code samples for 6 scenarios
- [Validation](./references/api-validation.md) — A1 notation rules, limits, enums, error codes
