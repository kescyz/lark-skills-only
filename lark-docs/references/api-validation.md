# Lark Docs Validation Reference

> See [api-reference.md](./api-reference.md) for method signatures.
> See [api-examples.md](./api-examples.md) for code samples.

---

## Block Type Enum

**IMPORTANT:** All block types MUST include their corresponding key even if the value is empty.
E.g., divider needs `{"block_type": 22, "divider": {}}`, NOT just `{"block_type": 22}`.
Heading block_type 3 uses key `heading1`, block_type 4 uses `heading2`, etc. (NOT `heading` + `level`).

| ID | Type | Key in block object | Can have children |
|----|------|---------------------|-------------------|
| 1 | Page | `page` | Yes (root block) |
| 2 | Text | `text` | No |
| 3-11 | Heading 1-9 | `heading1`-`heading9` | No |
| 12 | Bullet List | `bullet` | No |
| 13 | Ordered List | `ordered` | No |
| 14 | Code Block | `code` | No | Defaults to `language=1` (PlainText) if omitted |
| 15 | Quote | `quote` | No |
| 17 | Todo | `todo` | No |
| 18 | Bitable | `bitable` | No | Create with `view_type`: 1=DataSheet, 2=Kanban. Token auto-generated, readonly |
| 19 | Callout | `callout` | Yes | Optional `emoji_id` for icon |
| 22 | Divider | `divider` | No | **Must include `"divider": {}`** |
| 23 | File | `file` | No | Use file_token field (not token). Upload media (parent_type=docx_file, parent_node=doc_id) first |
| 24 | Grid | `grid` | Yes (auto-creates N `grid_column` children) |
| 25 | Grid Column | `grid_column` | Yes |
| 27 | Image | `image` | No | Token from media upload. Workflow: create empty block → upload media (parent_node=block_id, parent_type=docx_image) → batch_update replace_image |
| 30 | Sheet | `sheet` | No | Create with `row_size` + `column_size` (max 9×9). Token auto-generated, readonly. Edit via Sheets API: SpreadsheetToken_SheetID. Formulas: `{"type": "formula", "text": "=SUM(A1:A5)"}` NOT plain string |
| 31 | Table | `table` | Yes (table cells) | Static display — use for reports/specs. For formulas/interactive: use Sheet (30) |
| 32 | Table Cell | `table_cell` | Yes |
| 33 | View | `view` | No | Auto-created wrapper — NOT directly creatable |
| 34 | Quote Container | `quote_container` | Yes |
| 35 | Task | `task` | No | Read-only embed — returns task_id only. Cannot create/edit tasks via DocX API |
| 43 | Board | `board` | No | Create with empty object `{}`. Token (whiteboard_id) auto-generated, readonly. Screenshot: `GET /board/v1/whiteboards/:id/download_as_image` (scope: board:whiteboard:node:read) |
| 53 | Reference Base | `reference_base` | No | Bitable view embed with specific view_id. Read-only, auto-created |
| 999 | Tasklist embed | — | No | UI-only block (tasklist) — NOT supported by API, cannot create |

---

## Parent-Child Rules

| Parent Type | Allowed Children |
|-------------|-----------------|
| Page (1) | Text, Heading, Bullet, Ordered, Code, Quote, Todo, Callout, Divider, Grid, Table, Image, File, Bitable, Quote Container |
| Callout (19) | Text, Heading, Bullet, Ordered, Code, Quote, Todo, Divider, Image |
| Grid (24) | Grid Column only |
| Grid Column (25) | Same as Page (except Grid) |
| Table (31) | Table Cell only |
| Table Cell (32) | Text, Heading, Bullet, Ordered, Todo |
| Quote Container (34) | Text, Heading, Bullet, Ordered, Code, Todo |

---

## Text Element Types

```
text_element
├── text_run        # Plain text with optional style
│   ├── content     # string (required)
│   └── text_element_style
│       ├── bold, italic, strikethrough, underline, inline_code  # bool
│       ├── background_color  # int 1-15
│       ├── text_color        # int 1-7
│       └── link              # {url: string} (url-encoded)
├── mention_user    # @user
│   └── user_id     # OpenID string
├── mention_doc     # @document
│   ├── token       # document token
│   ├── obj_type    # 1=doc, 3=sheet, 8=bitable, 12=slides, 15=mindnote, 16=docx, 22=wiki
│   └── url         # document URL
├── equation        # LaTeX equation
│   └── content     # LaTeX string
└── reminder        # Date reminder
    ├── create_user_id  # creator OpenID
    ├── expire_time     # MILLISECONDS (13-digit timestamp)
    └── notify_time     # MILLISECONDS (13-digit timestamp)
```

---

## TextStyle (block-level style)

```
style
├── align       # 1=left, 2=center, 3=right
├── done        # bool (todo blocks only)
├── folded      # bool (collapsible blocks)
├── language    # int 1-75 (code blocks only, see language enum)
└── wrap        # bool (code block auto-wrap)
```

---

## Field Constraints

| Field | Constraint |
|-------|-----------|
| title | 1-800 characters |
| children (create_blocks) | 1-50 blocks per call |
| requests (batch_update) | Max 200 per call |
| page_size (list/get_children) | Max 500 |
| heading level | 1-9 (maps to block_type 3-11) |
| delete index range | [start_index, end_index) — left-closed, right-open |
| document_id | 27 characters |
| link url | Must be URL-encoded |
| Reminder timestamps | MILLISECONDS (13 digits) |

---

## Table Constraints

| Constraint | Value | Notes |
|-----------|-------|-------|
| Max cells at creation | ~29 | 28 OK (7×4), 30 FAIL (10×3). Exact boundary is 29 |
| Max rows/cols after grow | No known limit | Tested 15×4=60 cells via `insert_table_row` |
| Cell auto-content | 1 empty text block per cell | Auto-generated at creation. Use `update_block` to fill, NOT `create_blocks` (which adds extra blank line) |
| Grow table | `insert_table_row` / `insert_table_column` | Via `batch_update_blocks`. No cell limit |
| Shrink table | `delete_table_rows` / `delete_table_columns` | Via `batch_update_blocks` |
| Merge cells | `merge_table_cells` | Via `batch_update_blocks` |
| Cell content types | Text, Heading, Bullet, Ordered, Todo | No nested tables |

**Large table workflow:**
1. PRIMARY: Create small table (e.g., 2xN, under 29-cell limit), then `insert_table_row` to reach target rows, then `fill_table_cells` to populate content. Reliable and predictable.
2. ALTERNATIVE: `convert_to_blocks` from markdown - handles large tables but requires complex reconstruction: filter out type-32 table_cell blocks, create empty table shell, then map and fill cells separately.

**Convert output cleanup rules (all required for create_blocks):**
- Strip `block_id`, `parent_id`, `children` from every block
- Filter out `table_cell` (block_type 32) - fails entire batch if included
- Remove `merge_info` from `table.property` and `cells` from `table`
- Use `LarkDocsClient.clean_convert_output(blocks)` for automatic cleanup
- Block order unreliable for large docs (500+ lines) - use manual parsing instead

**Table vs Sheet:**
- Table (31): static display — reports, quotations, specifications
- Sheet (30): interactive — formulas, filter/sort, charts, live calculations
  - Sheet formulas use `{"type": "formula", "text": "=SUM(A1:A5)"}` — NOT plain string
  - Edit via Sheets API using `SpreadsheetToken_SheetID` from block token

---

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Write ops (create/update/delete blocks) | 3/sec per document |
| Read ops (get/list) | 5/sec per app |
| App-level API calls | 3/sec per endpoint |

**Retry**: Exponential backoff (2s, 4s, 8s) built into `LarkAPIBase` for code 1254290.

---

## Error Code Reference

| Code | HTTP | Message | Fix |
|------|------|---------|-----|
| 0 | 200 | Success | — |
| 1770001 | 400 | Invalid param | Check field names/types/required |
| 1770002 | 404 | Not found | Document deleted or wrong ID |
| 1770003 | 400 | Resource deleted | Resource no longer exists |
| 1770004 | 400 | Too many blocks | Document block limit exceeded |
| 1770005 | 400 | Too deep level | Block nesting depth exceeded |
| 1770006 | 400 | Schema mismatch | Invalid document structure |
| 1770007 | 400 | Too many children | Max children per block exceeded |
| 1770010 | 400 | Too many table columns | Table column limit exceeded |
| 1770011 | 400 | Too many table cells | Table cell limit exceeded |
| 1770012 | 400 | Too many grid columns | Grid column limit exceeded |
| 1770014 | 400 | Parent-child mismatch | Invalid block nesting relationship |
| 1770022 | 400 | Invalid page_token | Bad pagination token |
| 1770024 | 400 | Invalid operation | Check operation type |
| 1770025 | 400 | Op/block mismatch | Wrong operation for block type |
| 1770028 | 400 | No children allowed | Block type can't have children |
| 1770029 | 400 | Block can't be created | Block type not supported for creation |
| 1770031 | 400 | Can't delete children | Block type doesn't support child deletion |
| 1770032 | 403 | Forbidden | Check document permissions |
| 1770036 | 400 | Folder locked | Serialize document creation in same folder |
| 1770039 | 404 | Folder not found | Check folder_token |
| 1770040 | 403 | No folder permission | No create permission in folder |
| 1771001 | 500 | Server error | Retry |
| 1771005 | 503 | Under maintenance | Wait and retry |
| 99991663 | 401 | Token expired | MCP `refresh_lark_token` |
| 99991664 | 403 | Permission denied | Check app scopes |
| 1254290 | 429 | Rate limited | Backoff (2s, 4s, 8s) |
