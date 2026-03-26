---
name: lark-docs
description: LarkSuite document creation and block-level editing via DocX API. Use when user asks about creating or editing Lark documents. Requires lark-token-manager MCP.
---

# Lark Docs

Create and edit LarkSuite documents: create docs, add text/headings/todos,
read content, update blocks, and manage document structure via DocX block tree.

## Prerequisites

- `lark-token-manager` MCP server configured
- Lark app scopes:
  - `docx:document` — create/edit docs, blocks, nested blocks
  - `docx:document:readonly` — read-only access
  - `docx:document.block:convert` — convert_to_blocks (separate, must add explicitly)
  - `drive:drive` — media upload (images/files)
  - `board:whiteboard:node:read` — board screenshot download
  - `sheets:spreadsheet` — edit embedded sheet blocks via Sheets API
  - `bitable:app` — edit embedded bitable blocks via Base API

## Initialization

### Step 1: Get user info
MCP `whoami` -> `linked_users[].lark_open_id` -> user_open_id

### Step 2: Get token
MCP `get_lark_token(app_name)` -> ACCESS_TOKEN
- If expired: MCP `refresh_lark_token` -> if fails: MCP `start_oauth`

### Step 3: Init client
```python
import sys, os

# Find scripts path relative to SKILL.md location
skill_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(skill_dir, 'scripts'))

from lark_api import LarkDocsClient

client = LarkDocsClient(access_token=ACCESS_TOKEN, user_open_id=OPEN_ID)
```

## Encoding (Non-ASCII Data)

ALWAYS use the Python scripts (`scripts/`) for ALL API calls. NEVER use `curl` in Bash for requests containing non-ASCII characters (Vietnamese, Chinese, Japanese, etc.). Windows terminal encoding (cp1252) corrupts UTF-8 data, causing mojibake. The Python scripts use `urllib.request` with proper `ensure_ascii=False` encoding - this is the correct and safe approach.

**Windows users:** Set `PYTHONIOENCODING=utf-8` before running scripts to avoid `UnicodeEncodeError` when printing non-ASCII output. Example: `PYTHONIOENCODING=utf-8 python3 script.py`

## Decision Guide

```
Create new document?               -> client.create_document(title, folder_token)
Get document info?                 -> client.get_document(document_id)
Read plain text content?           -> client.get_raw_content(document_id)
Export doc to markdown?            -> client.export_to_markdown(document_id)
Export with images/files?          -> client.export_to_markdown(document_id, download_media=True, save_dir="./out")
List all blocks in doc?            -> client.list_blocks(document_id)

Get a specific block?              -> client.get_block(document_id, block_id)
Get children of a block?           -> client.get_block_children(document_id, block_id)
Add blocks to document?            -> client.create_blocks(document_id, parent_id, children)
Update block content?              -> client.update_block(document_id, block_id, ...)
Batch update multiple blocks?      -> client.batch_update_blocks(document_id, requests)
Delete blocks by index?            -> client.delete_blocks(document_id, parent_id, start, end)

Quick add text?                    -> client.create_text_block(document_id, parent_id, text)
Quick add heading?                 -> client.create_heading_block(document_id, parent_id, text, level)
Quick add todo?                    -> client.create_todo_block(document_id, parent_id, text, done)
Add @mention to todo/text?         -> use mention_user element: {"mention_user": {"user_id": open_id}}

Create table (≤29 cells)?         -> client.create_table(document_id, parent_id, rows, cols)
Create large table (>29 cells)?   -> PRIMARY: create_table(2, N) + insert_table_row + fill_table_cells
                                      ALTERNATIVE: convert_to_blocks (complex reconstruction needed)
Add row to table?                  -> client.insert_table_row(document_id, table_id, row_index)
Add column to table?               -> client.insert_table_column(document_id, table_id, col_index)
Delete rows from table?            -> client.delete_table_rows(document_id, table_id, start, end)
Merge table cells?                 -> client.merge_table_cells(document_id, table_id, r0, r1, c0, c1)
Fill table cells?                  -> client.fill_table_cells(document_id, table_id, data_rows)

Upload image to doc?               -> 3-step: create empty image → media upload (parent_node=block_id, parent_type=docx_image) → replace_image
Attach file to doc?                -> media upload (parent_node=doc_id, parent_type=docx_file) → create file block with file_token
Import markdown/HTML to doc?        -> client.import_markdown(doc_id, markdown_str) (one-call, handles tables)
Convert markdown to blocks?        -> client.convert_to_blocks(content) then clean_convert_output(blocks, for_descendant=True)
Insert many blocks (up to 1000)?   -> client.create_nested_blocks(doc_id, doc_id, first_level_ids, cleaned_blocks)
Create bitable block?              -> create_blocks with block_type 18, view_type: 1=DataSheet 2=Kanban (token auto-generated, readonly)
Create sheet block?                -> create_blocks with block_type 30, row_size + column_size (max 9×9, token auto-generated)
Edit embedded sheet?               -> Sheets API using SpreadsheetToken_SheetID from block. Formulas: {"type": "formula", "text": "=SUM(...)"}
Create board block?                -> create_blocks with block_type 43, {"board": {}} (whiteboard_id auto-generated, readonly)
Get board screenshot?              -> GET /board/v1/whiteboards/:id/download_as_image (scope: board:whiteboard:node:read)
Create todo with @assign?          -> todo block with mention_user element: {"mention_user": {"user_id": open_id}}
Create task block?                 -> Task(35) is READ-ONLY. Tasklist embed (999) is UI-only. Use Todo for task-like items.

TABLE vs SHEET choice:
  Table (31) = static display     -> reports, specs, quotations, comparison tables
  Sheet (30) = interactive        -> formulas, filter/sort, charts, live calculations

Content insertion strategy:
  Markdown/HTML (any size):       -> import_markdown(doc_id, content) (RECOMMENDED - uses descendant, handles tables)
  Few blocks (1-50):              -> create_blocks (RELIABLE)
  Many blocks (50-300):           -> create_blocks in batches of 50 with 0.4s delay
  Large table (>29 cells):        -> create_large_table(doc_id, parent_id, rows, cols, data_rows)
  Tables from markdown:           -> create_table + insert_table_row + fill_table_cells (programmatic)
  Nested blocks (up to 1000):     -> create_nested_blocks(doc_id, doc_id, top_level_ids, descendants)
```

## API Methods (25 client methods + media upload APIs)

### Convert & Import (4)
| Method | Description |
|--------|-------------|
| `import_markdown(doc_id, content, content_type="markdown")` | One-call markdown/HTML to doc. Uses descendant endpoint (tables work). Fallback to create_blocks batches |
| `convert_to_blocks(content, content_type="markdown")` | Convert markdown/html to blocks. Scope: `docx:document.block:convert`. Returns blocks + first_level_block_ids |
| `clean_convert_output(blocks, for_descendant=False)` | Static. `for_descendant=True`: only removes merge_info (keeps block_id/children for tree). `False`: strips IDs, filters table_cell(32) |
| `create_nested_blocks(doc_id, block_id, children_id, descendants, index)` | Insert up to 1000 nested blocks. children_id: use first_level_block_ids from convert output |

### Document (4)
| Method | Description |
|--------|-------------|
| `create_document(title=None, folder_token=None)` | Create doc, returns `{document: {document_id, revision_id, title}}` |
| `get_document(document_id)` | Get metadata (document_id, revision_id, title) |
| `get_raw_content(document_id, lang=0)` | Plain text content. lang: 0=all, 1=zh, 2=en, 3=ja |
| `list_blocks(document_id)` | All blocks in doc tree (paginated, auto-fetches) |

### Export (1)
| Method | Description |
|--------|-------------|
| `export_to_markdown(document_id, download_media=False, save_dir=None)` | Export doc to markdown. Downloads images/files/board screenshots when `download_media=True`. Renders tables, todos, headings, code, quotes. Placeholders for Sheet/Bitable/Task embeds. |

### Block (6)
| Method | Description |
|--------|-------------|
| `get_block(document_id, block_id)` | Single block with content |
| `get_block_children(document_id, block_id)` | Direct children (paginated) |
| `create_blocks(document_id, block_id, children, index=None)` | Create 1-50 child blocks under parent |
| `update_block(document_id, block_id, update_text_elements=None, ...)` | Update block content (one op type per call) |
| `batch_update_blocks(document_id, requests)` | Batch update up to 200 blocks |
| `delete_blocks(document_id, block_id, start_index, end_index)` | Delete children by index range [start, end) |

### Convenience (3)
| Method | Description |
|--------|-------------|
| `create_text_block(document_id, parent_block_id, text, bold, italic)` | Quick text block |
| `create_heading_block(document_id, parent_block_id, text, level=1)` | Heading level 1-9 |
| `create_todo_block(document_id, parent_block_id, text, done=False)` | Todo/checklist block |

### Table (7)
| Method | Description |
|--------|-------------|
| `create_large_table(doc_id, parent_id, rows, cols, data_rows, index)` | Create any-size table with data. Auto-handles >29 cell limit |
| `create_table(document_id, parent_id, row_size, column_size)` | Create table (max ~29 cells) |
| `insert_table_row(document_id, table_id, row_index)` | Insert row (no cell limit) |
| `insert_table_column(document_id, table_id, column_index)` | Insert column |
| `delete_table_rows(document_id, table_id, start, end)` | Delete rows [start, end) |
| `merge_table_cells(document_id, table_id, r0, r1, c0, c1)` | Merge cell range |
| `fill_table_cells(document_id, table_id, data_rows)` | Fill all cells (batch update) |

**Table gotchas:**
- Create limit: ~29 cells. Bypass: `create_table(2, N)` + `insert_table_row` loop (RELIABLE)
- `convert_to_blocks` can handle large tables but requires complex reconstruction (filter type-32 cells, map positions, fill separately)
- Each cell auto-generates 1 empty text block. Use `update_block` / `fill_table_cells` to fill (NOT `create_blocks`, which adds extra blank line)
- `fill_table_cells` accepts `data_rows`: list of rows, each row is list of `str` or `{"text": str, "bold": bool}`

## Key Constraints

- **Service path is `docx`** (not `docs`): all URLs use `/open-apis/docx/v1/`
- **Block tree model**: documents are trees of typed blocks; page block_id == document_id
- **Block JSON key must match block_type**: heading1 (type 3) uses key `heading1`, NOT `heading` + level. Divider (type 22) needs `"divider": {}`. All block types must include their key even if empty.
- **No delete document API** in DocX — use Drive API (see Cross-Domain below)
- **Write rate limit**: 3 edits/sec per document (create, update, batch_update, delete blocks)
- **Read rate limit**: 5 reads/sec per app
- **`delete_blocks` uses index range** [start, end) on parent's children, NOT block IDs
- **`create_blocks` limit**: 1-50 children per call
- **`batch_update_blocks` limit**: max 200 requests per call
- **`create_nested_blocks` limit**: up to 1000 blocks per call (use `/descendant` endpoint)
- **Timestamps**: MILLISECONDS (13 digits) for Reminder elements
- **Media Upload**: field is `parent_node` (NOT `parent_token`). Image: `parent_node=block_id`, File: `parent_node=doc_id`
- **Convert scope**: `docx:document.block:convert` is separate from `docx:document` — must be added explicitly
- **Convert field names**: use `content_type` (not `source_type`) and `content` (not `source`)
- **Convert + descendant workflow** (official per Lark API docs):
  1. `convert_to_blocks(markdown)` -> get `blocks` + `first_level_block_ids`
  2. `clean_convert_output(blocks, for_descendant=True)` -> only removes `merge_info`
  3. `create_nested_blocks(doc_id, doc_id, first_level_block_ids, cleaned_blocks)`
  Or use `import_markdown(doc_id, content)` for all-in-one.
- **Convert + create_blocks fallback** (when descendant fails):
  `clean_convert_output(blocks, for_descendant=False)` -> strips block_id/parent_id/children, filters table_cell(32), removes cells. Tables become empty shells - fill via `fill_table_cells`.
- **create_nested_blocks**: `children_id` must contain 1-1000 temp IDs from `first_level_block_ids` (NOT empty list). Supports tables with nested cells. `document_revision_id` is query param.
- **Bitable (18), Sheet (30), Board (43)**: directly creatable — tokens are auto-generated, readonly. Do NOT supply token in payload.

## Cross-Domain Operations

**Delete document**: `DELETE /open-apis/drive/v1/files/{document_id}?type=docx`
**Share document**: `POST /open-apis/drive/v1/permissions/{document_id}/members` with `{member_type, member_id, perm}`
**Move document**: `POST /open-apis/drive/v1/files/{document_id}/move` with `{type: "docx", folder_token}`

These use the same ACCESS_TOKEN. Activate `lark-drive` skill for full Drive operations.

## Personnel Lookup

Use MCP tools directly - no Python needed:

**Find specific people:**
```
search_users(query="Name") -> [{name, email, department, lark_open_id, ...}]
```

**List department members:**
```
list_departments() -> [{department_id, name, ...}]
list_department_users(department_id) -> [{user_id, open_id, name, ...}]
```

Use `lark_open_id` for sharing with `member_type="openid"`.

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 99991663 | Token expired | `refresh_lark_token` via MCP |
| 1254290 | Rate limited | Backoff (2s, 4s, 8s) |
| 1770001 | Invalid param | Check request body |
| 1770002 | Not found | Document may be deleted |
| 1770032 | Forbidden | Check document permissions |
| 1770039 | Folder not found | Check folder_token |

## Constructing URLs

| Type | URL Pattern |
|------|-------------|
| Document | `https://{org}.larksuite.com/docx/{document_id}` |
| Wiki page | `https://{org}.larksuite.com/wiki/{node_token}` |

Get org slug from MCP `whoami` → `organizations[].org_slug`.

## References

- [api-reference.md](./references/api-reference.md) — Full method params, return types
- [api-examples.md](./references/api-examples.md) — Code samples for common scenarios
- [api-validation.md](./references/api-validation.md) — Block types, constraints, error codes