# Agent Guide: Content -> Lark Doc Block Fragmentation

How to decompose user content into a Lark Doc block tree before calling the DOCX Block API.

## Core Concepts

- Lark Docs are **block trees**: Page (root) -> child blocks -> nested children
- **42 block types** available (text, heading, code, table, callout, image, etc.)
- Create doc empty first via `POST /docx/v1/documents`, then populate blocks
- Max **50 children** per create request. Rate: **3 req/s** per doc
- Batch update: **200 blocks** max per request

## Block Type Mapping

### Markdown -> Lark Block

| Markdown | Block Type | Type ID | Notes |
|----------|-----------|---------|-------|
| `# Heading` | Heading1 | 4 | Heading1-9 = type 4-12 |
| `## Heading` | Heading2 | 5 | |
| `### Heading` | Heading3 | 6 | |
| Plain text / paragraph | Text | 2 | |
| `- item` | Bullet | 13 | |
| `1. item` | Ordered | 14 | |
| ` ```code``` ` | Code | 15 | 75 languages supported |
| `> quote` | Quote | 16 | |
| `- [ ] todo` | Todo | 17 | |
| `---` | Divider | 22 | No children |
| `![img](url)` | Image | 27 | Requires file_token from Drive upload |
| Table | Table | 18 | Needs TableCell children |
| Callout/admonition | Callout | 19 | Text-only children |

### Rich Text Styling

Text blocks support inline styling via `text_run` elements:

```json
{
  "block_type": 2,
  "text": {
    "elements": [
      {
        "text_run": {
          "content": "Bold text",
          "text_element_style": { "bold": true }
        }
      },
      {
        "text_run": {
          "content": " and normal text"
        }
      }
    ]
  }
}
```

Available styles: `bold`, `italic`, `strikethrough`, `underline`, `inline_code`, `text_color` (7 colors), `background_color` (15 colors), `link`.

## Parent-Child Constraints

### Allowed Nesting

| Parent | Allowed Children |
|--------|-----------------|
| Page (root) | Any block type |
| Text, Heading, Bullet, Ordered, Quote, Todo | Text blocks only (for nested lists) |
| Callout | Text blocks only (no tables, no media) |
| Table | TableCell only |
| TableCell | Text, Heading, Bullet, Ordered, Code, Quote, Todo |
| Grid | GridColumn only |
| GridColumn | Any except Table, Grid, Bitable |

### Forbidden Nesting

- Table inside TableCell (no nested tables)
- Grid inside GridColumn (no nested grids)
- Bitable inside any container
- Media blocks (Image, File) inside Callout
- Divider has no children

## Fragmentation Strategy

### Step 1: Parse Input Content

Identify content sections from user input (markdown, plain text, or structured data).

### Step 2: Map to Block Tree

```
User content:
  "# Project Plan
   Some intro text.
   - Item 1
   - Item 2
   ```python
   print('hello')
   ```"

Block tree:
  Page (root)
  ├── Heading1: "Project Plan"
  ├── Text: "Some intro text."
  ├── Bullet: "Item 1"
  ├── Bullet: "Item 2"
  └── Code: "print('hello')" (language: python)
```

### Step 3: Handle Tables

Tables require explicit structure:

```json
{
  "block_type": 18,
  "table": {
    "property": { "row_size": 2, "column_size": 3 },
    "cells": ["r0c0_id", "r0c1_id", "r0c2_id", "r1c0_id", "r1c1_id", "r1c2_id"]
  }
}
```

Each cell is a TableCell block containing text blocks. Create table first, then populate cells.

### Step 4: Batch in Groups of 50

If document has > 50 blocks at any level:

```python
children = [block1, block2, ..., block120]
for i in range(0, len(children), 50):
    batch = children[i:i+50]
    client._call_api("POST",
        f"/docx/v1/documents/{doc_id}/blocks/{parent_id}/children",
        data={"children": batch, "index": i}
    )
    time.sleep(0.35)  # Respect 3 req/s limit
```

### Step 5: Create Document Flow

```python
# 1. Create empty doc
doc = client.create_document("My Document", folder_token)
doc_id = doc["document"]["document_id"]

# 2. Get root block (Page)
blocks = client.list_blocks(doc_id)
root_id = blocks[0]["block_id"]  # Page block

# 3. Add children to root
client._call_api("POST",
    f"/docx/v1/documents/{doc_id}/blocks/{root_id}/children",
    data={"children": block_tree}
)
```

## Rate Limits

| Operation | Limit | Strategy |
|-----------|-------|----------|
| Create blocks | 3 req/s per doc | Sleep 0.35s between batches |
| Query blocks | 5 req/s per doc | Standard pagination |
| Batch update | 3 req/s, 200 blocks | Chunk updates |
| Concurrent edits | Max 3/s per doc | Sequential writes recommended |

## Common Error Codes

| Code | Meaning | Fix |
|------|---------|-----|
| 1770004 | Too many blocks | Split into smaller sections |
| 1770005 | Nesting too deep | Flatten block tree |
| 1770007 | Too many children in block | Batch in groups of 50 |
| 1770014 | Parent-child mismatch | Check constraint table above |

## Required Scopes

- `docx:document` — Create/edit upgraded docs
- `docx:document:readonly` — Read-only access
- `drive:drive` — For file uploads (images, attachments)
