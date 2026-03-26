# Lark Comment API Validation

## Required Scopes

| Scope | Purpose |
|---|---|
| `docs:doc` | Read/write comments on doc/docx files |
| `drive:drive` | Read/write comments on sheet/file types (full CRUD) |
| `drive:drive:readonly` | Read comments on doc/sheet/file types (read-only) |

Both `docs:doc` + `drive:drive` needed for full comment support across all file types. Use `drive:drive:readonly` if write access is not needed.

## file_type Enum

| Value | File Type |
|---|---|
| `doc` | Legacy Lark Doc |
| `docx` | New Lark Document (DocX) |
| `sheet` | Lark Spreadsheet |
| `file` | Generic drive file |

`bitable` is NOT supported — use base-specific APIs for Bitable comments.

## Rate Limits

- Comment read APIs: 100 req/min per app
- Comment write APIs: 50 req/min per app
- Error code `1254290` = rate limited → retry with exponential backoff (2s, 4s, 8s)

## Content Element Types

Used in `add_comment` and `add_reply` body (`elements` array):

| Type | Key | Required fields |
|---|---|---|
| Plain text | `text_run` | `text_run.text` (string) |
| @mention user | `mention_user` | `mention_user.user_id` (open_id), `mention_user.name` |
| @mention doc | `mention_doc` | `mention_doc.token`, `mention_doc.title`, `mention_doc.obj_type` |

Use `_build_text_elements(content)` helper for plain text. Build manually for mentions.

## Common Error Codes

| Code | Meaning | Action |
|---|---|---|
| `99991663` | Access token expired | `refresh_lark_token` then retry once |
| `1254290` | Rate limit exceeded | Exponential backoff: 2s, 4s, 8s |
| `230001` | File not found or no access | Verify file_token and user permissions |
| `230013` | Comment not found | Verify comment_id belongs to the file |
| `99991400` | Invalid file_type | Must be: doc, docx, sheet, file |

## Pagination

`list_comments` uses `_fetch_all` internally — handles `has_more` + `page_token` automatically. No manual pagination needed.

## Gotchas

- `solve_comment` returns empty data on success — `_call_api` returns `{}`, method returns `True`
- `list_comments` returns `[]` when no comments exist (safe — `_fetch_all` handles `items: null`)
- Global comments (`is_whole: true`) have no document position — inline comments have position metadata
- Reply content uses `elements` key (not `reply_list`) — different structure from `add_comment`
