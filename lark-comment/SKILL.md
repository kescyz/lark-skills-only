---
name: lark-comment
description: LarkSuite document comment management - add, list, reply, resolve comments on docs/sheets/files. Use when user asks about document comments, feedback, reviews, or comment threads. Requires lark-token-manager MCP.
---

# Lark Comment

Manage comments on LarkSuite documents (doc, docx, sheet, file).

## Prerequisites

- `lark-token-manager` MCP server configured in `.mcp.json`
- `LARK_SKILL_API_KEY` exported before launching Claude Code
- Lark app with `docs:doc` or `drive:drive` or `drive:drive:readonly` scope

## Initialization

### Step 1: Get user info from MCP

Call MCP `whoami` to get:
- `linked_users[].lark_open_id` -> user_open_id
- `linked_users[].lark_user_id` -> user_id

### Step 2: Get access token from MCP

Call MCP `get_lark_token(app_name=LARK_APP_NAME)`
- If expired: MCP `refresh_lark_token` -> if fails: MCP `start_oauth`

### Step 3: Initialize client

```python
import sys, os

# Find scripts path relative to SKILL.md location
skill_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(skill_dir, 'scripts'))

from lark_api import LarkCommentClient

client = LarkCommentClient(
    access_token=TOKEN_FROM_MCP,
    user_open_id=OPEN_ID_FROM_WHOAMI,
    user_id=USER_ID_FROM_WHOAMI
)
```

## Encoding (Non-ASCII Data)

ALWAYS use the Python scripts (`scripts/`) for ALL API calls. NEVER use `curl` in Bash for requests containing non-ASCII characters (Vietnamese, Chinese, Japanese, etc.). Windows terminal encoding (cp1252) corrupts UTF-8 data, causing mojibake. The Python scripts use `urllib.request` with proper `ensure_ascii=False` encoding - this is the correct and safe approach.

## API Methods

| Method | Description |
|--------|-------------|
| `add_comment(file_token, file_type, content, quote_content=None)` | Add a global comment to a file. `file_type`: doc, docx, sheet, file. `content`: plain text (auto-wrapped in element structure). Returns comment dict with `comment_id`. |
| `list_comments(file_token, file_type, is_whole=None, is_solved=None)` | List all comments on a file. Fetches all pages. Optional filters: `is_whole` (True = global only), `is_solved` (True/False). Returns list of comment dicts. |
| `add_reply(file_token, file_type, comment_id, content)` | Reply to an existing comment thread. Use `comment_id` from `list_comments` or `add_comment`. Returns reply dict with `reply_id`. |
| `solve_comment(file_token, file_type, comment_id, is_solved=True)` | Resolve or reopen a comment. Pass `is_solved=False` to restore. Returns `True` on success. |

## file_type Values

| Value | Document type |
|-------|--------------|
| `doc` | Legacy Docs |
| `docx` | New Docs (default for most documents) |
| `sheet` | Sheets / Spreadsheets |
| `file` | Files in My Space |

## Quick Examples

### Add comment to a doc
```python
comment = client.add_comment(
    file_token="doccnGp4UK1UskrOEJwBXd3****",
    file_type="docx",
    content="Please review this section."
)
comment_id = comment["comment_id"]
```

### List open comments
```python
comments = client.list_comments(
    file_token="doccnGp4UK1UskrOEJwBXd3****",
    file_type="docx",
    is_solved=False
)
for c in comments:
    print(c["comment_id"], c.get("reply_list", {}).get("replies", []))
```

### Reply to a comment
```python
reply = client.add_reply(
    file_token="doccnGp4UK1UskrOEJwBXd3****",
    file_type="docx",
    comment_id="6916106822734512356",
    content="Done, updated."
)
```

### Resolve a comment
```python
client.solve_comment(
    file_token="doccnGp4UK1UskrOEJwBXd3****",
    file_type="docx",
    comment_id="6916106822734512356",
    is_solved=True
)
```

## Content Element Structure

The API uses a structured `elements` array for content. This client auto-wraps plain text:

```python
# What the client sends internally for content="hello"
{"elements": [{"type": "text_run", "text_run": {"text": "hello"}}]}
```

To @mention a user or link a doc, use `_build_text_elements` directly or extend the `elements` list manually before calling `_call_api`.

## Required Scopes

At least one of:
- `docs:doc` — View, comment, edit, manage Docs
- `docs:doc:readonly` — View, comment, export Docs
- `drive:drive` — All files in My Space (full CRUD + comments)
- `drive:drive:readonly` — Read all files in My Space + read doc comments
- `sheets:spreadsheet` — Sheets (for sheet file_type)

## References

- [api-reference.md](./references/api-reference.md) — Full API reference (8 endpoints, including batch query, get single, get replies, update reply, delete reply)
