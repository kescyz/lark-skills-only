# Lark Docs API Reference

> Token management handled by `lark-token-manager` MCP server.
> See [api-examples.md](./api-examples.md) for code samples.
> See [api-validation.md](./api-validation.md) for block types, schemas, error codes.

## LarkDocsClient

```python
from lark_api import LarkDocsClient
client = LarkDocsClient(access_token="u-xxx", user_open_id="ou_xxx")
```

## Contents

- [Document Operations](#document-operations)
- [Block Operations](#block-operations)
- [Convenience Helpers](#convenience-helpers)
- [Table Helpers](#table-helpers)
- [Rate Limits](#rate-limits)
- [Error Codes](#error-codes)

---

## Document Operations

### create_document(title, folder_token)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| title | str | No | Document title | 1-800 chars |
| folder_token | str | No | Target folder | Empty = root dir |

**Returns**: `{"document": {"document_id": str, "revision_id": int, "title": str}}`

### get_document(document_id)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | 27 chars |

**Returns**: `{"document": {"document_id": str, "revision_id": int, "title": str}}`

### get_raw_content(document_id, lang)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| lang | int | No | Language filter | 0=all, 1=zh, 2=en, 3=ja |

**Returns**: `{"content": str}` — plain text of document

### list_blocks(document_id, page_size)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| page_size | int | No | Items per page | Max 500 (default) |

**Returns**: `List[block]` — all blocks, auto-paginates via `_fetch_all`

---

## Block Operations

### get_block(document_id, block_id)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| block_id | str | **Yes** | Block ID | — |

**Returns**: `{"block": {block_type, block_id, children_ids, parent_id, ...}}`

### get_block_children(document_id, block_id, page_size)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| block_id | str | **Yes** | Parent block ID | — |
| page_size | int | No | Items per page | Max 500 (default) |

**Returns**: `List[block]` — direct children, auto-paginates

### create_blocks(document_id, block_id, children, index)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| block_id | str | **Yes** | Parent block ID | Use document_id for root |
| children | list | **Yes** | Block objects to create | 1-50 items |
| index | int | No | Insert position | None = append |

Auto-sets `document_revision_id=-1` (latest version).

**Returns**: `{"children": [block, ...], "document_revision_id": int, "client_token": str}`

### update_block(document_id, block_id, update_text_elements, update_table_property, update_text_style)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| block_id | str | **Yes** | Block to update | — |
| update_text_elements | dict | No | `{"elements": [...]}` | 1+ elements |
| update_table_property | dict | No | Table property changes | — |
| update_text_style | dict | No | Text style changes | — |

Pass only ONE operation type per call.

**Returns**: `{"block": {updated_block}, "document_revision_id": int}`

### batch_update_blocks(document_id, requests)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| requests | list | **Yes** | Update requests | Max 200 items |

Each request: `{"block_id": str, "update_text_elements": {"elements": [...]}}`

**Returns**: `{"blocks": [...], "document_revision_id": int}`

### delete_blocks(document_id, block_id, start_index, end_index)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| block_id | str | **Yes** | Parent block ID | — |
| start_index | int | **Yes** | Start (inclusive) | >= 0 |
| end_index | int | **Yes** | End (exclusive) | >= 1 |

Deletes children at positions `[start_index, end_index)`.

**Returns**: `{"document_revision_id": int, "client_token": str}`

---

## Convenience Helpers

### create_text_block(document_id, parent_block_id, text, bold, italic)

Wraps `create_blocks` with single text block (block_type=2).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | str | **Yes** | Text content |
| bold | bool | No | Bold (default False) |
| italic | bool | No | Italic (default False) |

### create_heading_block(document_id, parent_block_id, text, level)

Wraps `create_blocks` with heading block. Level 1-9 maps to block_type 3-11.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | str | **Yes** | Heading text |
| level | int | No | 1-9 (default 1) |

### create_todo_block(document_id, parent_block_id, text, done)

Wraps `create_blocks` with todo block (block_type=17).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | str | **Yes** | Todo text |
| done | bool | No | Completed (default False) |

---

## Table Helpers

### create_table(document_id, parent_block_id, row_size, column_size, column_width)

Create a table block. Max ~29 cells at creation. For larger tables, create small then use `insert_table_row`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| row_size | int | **Yes** | Number of rows |
| column_size | int | **Yes** | Number of columns |
| column_width | list[int] | No | Column widths in pixels |

### insert_table_row(document_id, table_block_id, row_index)

Insert a new row at `row_index`. New cells auto-generate with empty text blocks.

### insert_table_column(document_id, table_block_id, column_index)

Insert a new column at `column_index`.

### delete_table_rows(document_id, table_block_id, row_start_index, row_end_index)

Delete rows in range `[start, end)`.

### merge_table_cells(document_id, table_block_id, row_start, row_end, col_start, col_end)

Merge cells in range `[row_start, row_end) × [col_start, col_end)`.

### fill_table_cells(document_id, table_block_id, data_rows)

Fill table cells with content. `data_rows` is list of rows, each row is list of `str` or `{"text": str, "bold": bool}`.

Uses `list_blocks()` + `batch_update_blocks` to update existing empty text blocks (avoids extra blank lines).

---

## Export

### export_to_markdown(document_id, download_media=False, save_dir=None)

Export entire document to a markdown string.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| document_id | str | **Yes** | Document ID |
| download_media | bool | No | Download images/files/board screenshots (default False) |
| save_dir | str | No | Directory to save media files (required if download_media=True) |

**Returns**: `str` — formatted markdown

**Renders**: text, headings(1-9), bullet, ordered, code(19 languages), quote, todo(with checkbox), divider, table(full markdown), callout, grid, quote_container, image, file, board screenshot

**Placeholders**: Sheet(30) `> 📋 Embedded Sheet`, Bitable(18) `> 📊 Embedded Bitable`, Task(35) `> 📋 Task: id`

**Not supported**: Tasklist embed (block 999) — API returns no data

---

## Media Upload

### upload_media(document_id, block_id, file_path, parent_type)

Upload a media file for use in Image or File blocks via `POST /drive/v1/medias/upload_all`.

**CRITICAL**: The field is `parent_node` NOT `parent_token`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| document_id | str | **Yes** | Document ID |
| block_id | str | **Yes** | Block ID or doc ID (see parent_type) |
| file_path | str | **Yes** | Local path to media file |
| parent_type | str | **Yes** | `docx_image` or `docx_file` |

**Returns**: `{"file_token": str}`

#### Image block — 3-step workflow

1. `create_blocks` with empty image placeholder:
   ```json
   {"block_type": 27, "image": {"token": "", "width": 100, "height": 100}}
   ```
2. Upload media — `parent_node=block_id`, `parent_type=docx_image`
3. `batch_update_blocks` with `replace_image` operation:
   ```json
   {"block_id": image_block_id, "replace_image": {"token": file_token}}
   ```

#### File block — 2-step workflow

1. Upload media — `parent_node=doc_id`, `parent_type=docx_file`
2. `create_blocks` with file token in `file_token` field (NOT `token`):
   ```json
   {"block_type": 23, "file": {"file_token": media_token}}
   ```

---

## Convert To Blocks

### POST /docx/v1/documents/blocks/convert

Convert markdown or HTML source to Lark block JSON for insertion. Client method: `convert_to_blocks(content, content_type)`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| content_type | string | **Yes** | `"markdown"` or `"html"` |
| content | str | **Yes** | Markdown or HTML content |

**Scope required**: `docx:document.block:convert`

**Returns**: `{"blocks": [block, ...]}` - array of block objects with block_id, parent_id, children fields

**Supported types**: text, heading(1-9), bullet, ordered, code, quote, todo, image, table, table_cell

**CRITICAL - Convert output requires cleanup before insertion via `create_blocks`:**
1. Strip `block_id`, `parent_id`, `children` from every block (causes schema mismatch)
2. Filter out `table_cell` (block_type 32) blocks (causes "block not support to create")
3. Remove `merge_info` from `table.property` AND `cells` from `table` (causes invalid param)

Use `LarkDocsClient.clean_convert_output(blocks)` to handle all steps automatically.

**WARNING**: Block order is unreliable for large documents (500+ lines). For large docs, parse markdown manually and use `create_blocks` directly.

---

## Create Nested Blocks

### POST /docx/v1/documents/:doc_id/blocks/:block_id/descendant

Insert up to 1000 nested blocks per call (vs 50 limit for `create_blocks`). Client method: `create_nested_blocks()`

Use `children_id` with `first_level_block_ids` from `convert_to_blocks` output for reliable insertion order.

**Body parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| children_id | string[] | **Yes** | Top-level block IDs - use `first_level_block_ids` from convert output. **Must contain 1-1000 items (NOT empty list)**. Server maps these to actual block IDs |
| descendants | block[] | **Yes** | All block objects with parent-child tree structure (block_id + children fields) |
| index | int | No | Insertion position. -1=last (default), 0=first |

**Query parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| document_revision_id | int | No | -1 for latest (default). **This is a query param, NOT body field** |

**Scope required**: `docx:document`

---

## Import Markdown

### POST /docx/v1/documents/import (client method: `import_markdown`)

Import a markdown string directly into a new or existing document. Converts markdown syntax to DocX blocks server-side.

**Body parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | No | Document title. If omitted, uses first heading from markdown |
| markdown | string | **Yes** | Markdown content to import |
| folder_token | string | No | Destination folder. Omit for My Drive root |

**Response**: `document_id` of the created/updated document.

**Scope required**: `docx:document`

---

## Create Large Table

### Client method: `create_large_table`

Create a table with more than 29 cells (the single-call creation limit) by combining `create_blocks` + `batch_update_blocks` to grow the table row by row, then fill cells via `update_block`.

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| doc_id | string | **Yes** | Target document ID |
| parent_id | string | **Yes** | Parent block ID |
| rows | int | **Yes** | Total row count |
| cols | int | **Yes** | Total column count |
| data | list[list[str]] | No | 2D array of cell text values |

**How it works:**
1. Create table shell via `create_blocks` (uses max 29-cell safe limit: 3 rows x cols)
2. Grow to target row count via repeated `insert_table_row` in `batch_update_blocks`
3. Fill all cells via `update_block` with text content

**Scope required**: `docx:document`

---

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Write (create/update/delete blocks) | 3/sec per document |
| Read (get/list) | 5/sec per app |
| App-level calls | 3/sec per endpoint |

**Retry**: Exponential backoff (2s, 4s, 8s) built into `LarkAPIBase`.

---

## Error Codes

| Code | HTTP | Message | Fix |
|------|------|---------|-----|
| 0 | 200 | Success | Continue |
| 1770001 | 400 | Invalid param | Check request body fields |
| 1770002 | 404 | Not found | Document may be deleted |
| 1770003 | 400 | Resource deleted | Resource no longer exists |
| 1770004 | 400 | Too many blocks | Max blocks per document exceeded |
| 1770007 | 400 | Too many children | Max children per block exceeded |
| 1770014 | 400 | Parent-child mismatch | Invalid block nesting |
| 1770028 | 400 | Block can't have children | Block type doesn't support children |
| 1770032 | 403 | Forbidden | Check document permissions |
| 1770039 | 404 | Folder not found | Check folder_token |
| 1770040 | 403 | No folder permission | No create permission in folder |
| 1771001 | 500 | Server error | Retry |
| 99991663 | 401 | Token expired | MCP `refresh_lark_token` |
| 99991664 | 403 | Permission denied | Check app scopes |
| 1254290 | 429 | Rate limited | Backoff (2s, 4s, 8s) |
