# Lark Docs API Examples

> All examples assume the client is initialized per [SKILL.md](../SKILL.md).
> See [api-reference.md](./api-reference.md) for param details.
> See [api-validation.md](./api-validation.md) for block types and error codes.

---

## 1. Create Document and Add Content

```python
# Create document
result = client.create_document(title="Meeting Notes")
doc_id = result["document"]["document_id"]

# Page block_id == document_id (root of block tree)
import time
time.sleep(1)  # rate limit: 3 writes/sec per doc

# Add heading
client.create_heading_block(doc_id, doc_id, "Action Items", level=1)
time.sleep(1)

# Add text
client.create_text_block(doc_id, doc_id, "Review Q3 targets", bold=True)
time.sleep(1)

# Add todo items
client.create_todo_block(doc_id, doc_id, "Update roadmap", done=False)
time.sleep(1)
client.create_todo_block(doc_id, doc_id, "Send follow-up email", done=True)
```

---

## 2. Read Document Content

```python
# Plain text content
raw = client.get_raw_content(doc_id)
print(raw.get("content", ""))

# Structured blocks
blocks = client.list_blocks(doc_id)
for b in blocks:
    btype = b.get("block_type")
    bid = b.get("block_id")
    print(f"  [{btype}] {bid}")
```

---

## 3. Create Complex Block Structure

```python
# Create multiple blocks in one call (1-50 per call)
blocks = [
    {
        "block_type": 3,  # heading1
        "heading1": {
            "elements": [{"text_run": {"content": "Section Title"}}]
        }
    },
    {
        "block_type": 2,  # text
        "text": {
            "elements": [
                {"text_run": {"content": "Normal text "}},
                {"text_run": {"content": "bold text", "text_element_style": {"bold": True}}},
            ]
        }
    },
    {
        "block_type": 12,  # bullet list
        "bullet": {
            "elements": [{"text_run": {"content": "First bullet point"}}]
        }
    },
]
result = client.create_blocks(doc_id, doc_id, blocks)
created = result.get("children", [])
print(f"Created {len(created)} blocks")
```

---

## 4. Update Block Text

```python
block_id = created[0]["block_id"]  # from previous create

client.update_block(doc_id, block_id, update_text_elements={
    "elements": [
        {"text_run": {"content": "Updated Section Title", "text_element_style": {"bold": True}}}
    ]
})
```

---

## 5. Batch Update Multiple Blocks

```python
requests = [
    {
        "block_id": block_id_1,
        "update_text_elements": {
            "elements": [{"text_run": {"content": "Updated text 1"}}]
        }
    },
    {
        "block_id": block_id_2,
        "update_text_elements": {
            "elements": [{"text_run": {"content": "Updated text 2"}}]
        }
    },
]
client.batch_update_blocks(doc_id, requests)  # max 200 per call
```

---

## 6. Delete Blocks by Index Range

```python
# Get children to see current order
children = client.get_block_children(doc_id, doc_id)
print(f"Before: {len(children)} children")

# Delete first 2 children [0, 2)
client.delete_blocks(doc_id, doc_id, start_index=0, end_index=2)

children = client.get_block_children(doc_id, doc_id)
print(f"After: {len(children)} children")
```

---

## 7. Create Large Table (bypass 29-cell creation limit)

```python
import time

# Step 1: Create small table (under 29-cell limit)
result = client.create_table(doc_id, doc_id, row_size=2, column_size=4)
table_id = result["children"][0]["block_id"]
time.sleep(1)

# Step 2: Grow to target rows via insert_table_row
target_rows = 14
for row_idx in range(2, target_rows):
    client.insert_table_row(doc_id, table_id, row_idx)
    time.sleep(0.4)

# Step 3: Fill cells (updates existing empty text blocks — no extra blank lines)
data_rows = [
    [{"text": "#", "bold": True}, {"text": "Feature", "bold": True},
     {"text": "Description", "bold": True}, {"text": "Cost", "bold": True}],
    ["A1", "Auth", "RBAC + 2FA", "38"],
    ["A2", "PWA", "Design system, responsive", "37"],
    # ... more rows
]
client.fill_table_cells(doc_id, table_id, data_rows)

# Step 4: Merge cells (optional)
client.merge_table_cells(doc_id, table_id, row_start=1, row_end=2, col_start=2, col_end=4)

# Step 5: Delete rows (optional)
client.delete_table_rows(doc_id, table_id, row_start_index=12, row_end_index=14)

# Step 6: Verify
raw = client.get_raw_content(doc_id)
print(raw.get("content", ""))
```

**Important notes:**
- Max ~29 cells at table creation. Use `insert_table_row` to grow beyond that.
- Each cell has an auto-generated empty text block. Use `fill_table_cells()` or
  `update_block()` to update it — do NOT use `create_blocks()` inside cells
  (causes extra blank line above content).
- `list_blocks()` returns ALL blocks including cell children — use it to find
  text block IDs for updating.

---

## 8. All Block Types — Minimum Valid JSON

```python
# All verified via live API. Use these as templates.

# TEXT-BEARING
{"block_type": 2, "text": {"elements": [{"text_run": {"content": "text"}}]}}
{"block_type": 3, "heading1": {"elements": [{"text_run": {"content": "H1"}}]}}  # heading1-heading9 (types 3-11)
{"block_type": 12, "bullet": {"elements": [{"text_run": {"content": "item"}}]}}
{"block_type": 13, "ordered": {"elements": [{"text_run": {"content": "item"}}]}}
{"block_type": 14, "code": {"elements": [{"text_run": {"content": "code"}}], "style": {"language": 49}}}  # 49=Python, default=1(PlainText)
{"block_type": 15, "quote": {"elements": [{"text_run": {"content": "quote"}}]}}
{"block_type": 17, "todo": {"elements": [{"text_run": {"content": "task"}}], "style": {"done": False}}}

# STRUCTURAL
{"block_type": 19, "callout": {"emoji_id": "star"}}      # container, add children after. emoji_id optional
{"block_type": 22, "divider": {}}                         # MUST include "divider": {} — omitting causes invalid param
{"block_type": 24, "grid": {"column_size": 2}}            # auto-creates N grid_column (25) children — do NOT add manually
{"block_type": 34, "quote_container": {}}                  # container

# TABLE (static display — for formulas/interactive use Sheet block type 30)
{"block_type": 31, "table": {"property": {"row_size": 2, "column_size": 2}}}  # max ~29 cells at creation

# RICH EMBEDS (tokens auto-generated, readonly via DocX API)
{"block_type": 18, "bitable": {"view_type": 1}}            # 1=DataSheet, 2=Kanban
{"block_type": 30, "sheet": {"row_size": 5, "column_size": 4}}  # max 9×9. Edit via Sheets API
{"block_type": 43, "board": {}}                            # whiteboard. Screenshot: GET /board/v1/whiteboards/:id/download_as_image

# IMAGE/FILE (via media upload — see Examples 10 for workflow)
{"block_type": 27, "image": {"token": "", "width": 100, "height": 100}}  # placeholder, then replace_image
{"block_type": 23, "file": {"file_token": "media_token"}}                # file_token NOT token
```

**Gotchas confirmed by testing:**
- Heading key must match type: `heading1` for type 3, NOT `heading` + level
- Divider without `"divider": {}` → `invalid param`
- Code defaults to `language=1` (PlainText) when style.language omitted
- Grid auto-creates `grid_column` children — do NOT create them manually
- Sheet formulas: use `{"type": "formula", "text": "=SUM(A1:A5)"}` NOT plain string
- Task (35): read-only embed — cannot create/edit via DocX API
- Block 53 (reference_base): Bitable view embed — auto-created, not directly creatable
- Block 999 (tasklist embed): UI-only, not supported by API

---

## 10. Image Block — Upload and Insert

3-step workflow: create empty image block → upload media → replace image token.

```bash
DOC_ID="your_document_id"
IMAGE_PATH="/path/to/image.png"
ACCESS_TOKEN="your_access_token"

# Step 1: Create empty image block (placeholder)
BLOCK_RESULT=$(curl -s -X POST \
  "https://open.larksuite.com/open-apis/docx/v1/documents/${DOC_ID}/blocks/${DOC_ID}/children" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [{"block_type": 27, "image": {"token": "", "width": 100, "height": 100}}],
    "document_revision_id": -1
  }')

IMAGE_BLOCK_ID=$(echo $BLOCK_RESULT | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['children'][0]['block_id'])")

# Step 2: Upload media — parent_node=IMAGE_BLOCK_ID, parent_type=docx_image
# CRITICAL: field is parent_node (NOT parent_token)
UPLOAD_RESULT=$(curl -s -X POST \
  "https://open.larksuite.com/open-apis/drive/v1/medias/upload_all" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -F "file_name=$(basename $IMAGE_PATH)" \
  -F "parent_type=docx_image" \
  -F "parent_node=${IMAGE_BLOCK_ID}" \
  -F "size=$(stat -c%s $IMAGE_PATH)" \
  -F "file=@${IMAGE_PATH}")

FILE_TOKEN=$(echo $UPLOAD_RESULT | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['file_token'])")

# Step 3: Replace image token via batch_update
curl -s -X PATCH \
  "https://open.larksuite.com/open-apis/docx/v1/documents/${DOC_ID}/blocks/batch_update" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"requests\": [{
      \"block_id\": \"${IMAGE_BLOCK_ID}\",
      \"replace_image\": {\"token\": \"${FILE_TOKEN}\"}
    }],
    \"document_revision_id\": -1
  }"
```

**Notes:**
- `parent_node` is the image block ID from Step 1 (NOT the doc ID)
- `parent_type` must be `docx_image` for image blocks
- Step 3 uses `replace_image` operation in `batch_update_blocks`

---

## 11. Convert Markdown to Blocks

Convert markdown to Lark block JSON, then insert into document.

```python
import time

# Step 1: Convert markdown to blocks (requires scope: docx:document.block:convert)
markdown_content = """
# Project Status

## Completed
- Feature A implemented
- Tests passing

## In Progress
- Feature B (50%)
"""

convert_result = client.convert_to_blocks(markdown_content)  # content_type: "markdown" (default) or "html"
blocks = convert_result.get("blocks", [])

# Step 2: Clean convert output (REQUIRED - handles ALL cleanup steps)
# - Strips block_id, parent_id, children from every block
# - Filters out table_cell (type 32) blocks
# - Removes merge_info from table.property and cells from table
blocks = LarkDocsClient.clean_convert_output(blocks)

# Step 3: Insert via create_blocks in batches of 50
for i in range(0, len(blocks), 50):
    batch = blocks[i:i + 50]
    result = client.create_blocks(doc_id, doc_id, batch)
    print(f"Batch {i // 50 + 1}: inserted {len(result.get('children', []))} blocks")
    if i + 50 < len(blocks):
        time.sleep(0.4)  # rate limit: 3 edits/sec per document
```

### 11b. Create Nested Blocks

The `/descendant` endpoint supports up to 1000 blocks per call.

```python
# For /descendant, keep block_id/children (tree structure needed)
blocks = LarkDocsClient.clean_convert_output(
    convert_result.get("blocks", []),
    for_descendant=True  # keeps block_id and children fields
)

# children_id = use first_level_block_ids from convert output (most reliable)
# Falls back to page block children if first_level_block_ids not present
top_level_ids = convert_result.get("first_level_block_ids") or []
if not top_level_ids:
    page_block = next((b for b in blocks if b.get("block_type") == 1), None)
    if page_block and page_block.get("children"):
        top_level_ids = page_block["children"]
    else:
        # Fallback: use all block IDs (flat insertion)
        top_level_ids = [b["block_id"] for b in blocks if b.get("block_id")]

result = client.create_nested_blocks(
    doc_id, doc_id,
    children_id=top_level_ids,
    descendants=blocks
)
```

**Notes:**
- `convert` scope (`docx:document.block:convert`) is separate from `docx:document` - app must have both
- Field names: `content_type` (not `source_type`) and `content` (not `source`)
- `clean_convert_output()` handles all cleanup: strip fields, filter type-32, clean tables
- **WARNING**: `convert_to_blocks` returns blocks in unreliable order for large docs (500+ lines). For large documents, parse markdown manually and use `create_blocks` directly
- Tables from convert output are created as empty shells (type-32 cell blocks are filtered). Use `fill_table_cells` to populate after creation

---

## 11c. Import Markdown

```python
# Import markdown string as a new Lark doc
markdown_content = """
# Project Status

## Completed
- Auth module
- User profile page

## In Progress
- Dashboard components
"""

result = client.import_markdown(
    markdown=markdown_content,
    title="Project Status",
    folder_token="FolderTokenABC"  # optional
)
doc_id = result.get("document_id")
print(f"Created doc: {doc_id}")
```

---

## 11d. Create Large Table

```python
# Create a table with more than 29 cells (e.g. 10 rows x 5 cols = 50 cells)
data = [
    ["Name", "Role", "Status", "Priority", "Notes"],
    ["Alice", "Engineer", "Active", "High", "Backend lead"],
    ["Bob", "Designer", "Active", "Medium", "UI components"],
    # ... more rows
]

result = client.create_large_table(
    doc_id=doc_id,
    parent_id=doc_id,
    rows=10,
    cols=5,
    data=data
)
print(f"Created table block: {result.get('block_id')}")
```

**Notes:**
- For tables > 29 cells, use `create_large_table` instead of `create_blocks` directly
- Internally: create 3-row shell, grow via `insert_table_row`, fill via `update_block`
- `data` is optional - omit to create empty table skeleton

---

## 12. Create Bitable, Sheet, Board Blocks

These block types are directly creatable — tokens are auto-generated and readonly (do not supply them).

```python
# Bitable — DataSheet view
{"block_type": 18, "bitable": {"view_type": 1}}

# Bitable — Kanban view
{"block_type": 18, "bitable": {"view_type": 2}}

# Sheet — embedded spreadsheet (max 9×9)
{"block_type": 30, "sheet": {"row_size": 5, "column_size": 4}}

# Board — whiteboard (empty object required)
{"block_type": 43, "board": {}}

# Example: insert all four into a document
result = client.create_blocks(doc_id, doc_id, [
    {"block_type": 18, "bitable": {"view_type": 1}},
    {"block_type": 30, "sheet": {"row_size": 5, "column_size": 4}},
    {"block_type": 43, "board": {}},
])
print(f"Created {len(result.get('children', []))} blocks")
```

**Notes:**
- Tokens (bitable token, sheet token, whiteboard_id) are auto-generated by Lark — do NOT include in creation payload
- Confirmed: previously documented as "embed only" — INCORRECT. All three are directly creatable.
- Sheet max dimensions: 9 rows × 9 columns
- Board uses empty `{}` object — no fields needed

---

## 13. Todo Block with @mention User

```python
# Todo with @assigned user (mention_user in elements)
todo_block = {
    "block_type": 17,
    "todo": {
        "elements": [
            {"text_run": {"content": "Review pull request "}},
            {"mention_user": {"user_id": "ou_xxxxx"}},  # @user OpenID
        ],
        "style": {"done": False}
    }
}
client.create_blocks(doc_id, doc_id, [todo_block])
```

---

## 14. Edit Embedded Sheet Block (formulas)

```python
# 1. Create sheet block (readonly via DocX API)
result = client.create_blocks(doc_id, doc_id, [
    {"block_type": 30, "sheet": {"row_size": 5, "column_size": 4}}
])
sheet_block = result["children"][0]
sheet_token = sheet_block.get("sheet", {}).get("token")  # e.g. "SpreadsheetToken_SheetID"

# 2. Edit via Sheets API (requires sheets:spreadsheet scope)
# Token format: "{spreadsheet_token}_{sheet_id}"
# Use lark-sheets skill for full Sheets API access

# Formula example (NOT plain string):
cell_with_formula = {"type": "formula", "text": "=SUM(A1:A5)"}
```

---

## 15. Board Screenshot

```bash
# Get screenshot of an embedded board block
# Requires scope: board:whiteboard:node:read
# whiteboard_id comes from board block token (auto-generated on creation)

curl -s -X GET \
  "https://open.larksuite.com/open-apis/board/v1/whiteboards/${WHITEBOARD_ID}/download_as_image" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  --output board_screenshot.png
```

---

## 9. Full Workflow: Create, Populate, Read Back

```python
import time

# 1. Create
result = client.create_document(title="Sprint Planning")
doc_id = result["document"]["document_id"]
time.sleep(1)

# 2. Add heading + items
client.create_heading_block(doc_id, doc_id, "Sprint Goals", level=1)
time.sleep(1)
client.create_text_block(doc_id, doc_id, "Deliver auth module by Friday")
time.sleep(1)
client.create_todo_block(doc_id, doc_id, "Design API schema")
time.sleep(1)
client.create_todo_block(doc_id, doc_id, "Write unit tests")
time.sleep(1)

# 3. Read back
raw = client.get_raw_content(doc_id)
print(raw.get("content", ""))

# 4. List blocks for structure
blocks = client.list_blocks(doc_id)
for b in blocks:
    indent = "  " if b.get("parent_id") == doc_id else "    "
    print(f"{indent}[{b['block_type']}] {b['block_id']}")
```
