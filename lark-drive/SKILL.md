---
name: lark-drive
description: LarkSuite Drive file management - upload, download, folders, permissions, search. Use when user asks about files, drive, uploads, or file sharing. Requires lark-token-manager MCP.
---

# Lark Drive

Manage Lark Drive: browse folders, upload/download files, create online docs, copy/move/delete, search, and manage sharing permissions.

## Prerequisites

- `lark-token-manager` MCP server configured
- `LARK_SKILL_API_KEY` exported before launching Claude Code
- Lark app scopes: `drive:drive` (full CRUD), `drive:drive:readonly` (read + doc comments), `drive:file` (upload/download)
- For search: `user_access_token` required (not tenant token)

## Initialization

### Step 1: Get user info
MCP `whoami` → `linked_users[].lark_open_id` → user_open_id

### Step 2: Get token
MCP `get_lark_token(app_name)` → ACCESS_TOKEN
- If expired: MCP `refresh_lark_token` → if fails: MCP `start_oauth`

### Step 3: Init client
```python
import sys, os

# Find scripts path relative to SKILL.md location
skill_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(skill_dir, 'scripts'))

from lark_api import LarkDriveClient
client = LarkDriveClient(access_token=ACCESS_TOKEN, user_open_id=OPEN_ID)
```

## Encoding (Non-ASCII Data)

ALWAYS use the Python scripts (`scripts/`) for ALL API calls. NEVER use `curl` in Bash for requests containing non-ASCII characters (Vietnamese, Chinese, Japanese, etc.). Windows terminal encoding (cp1252) corrupts UTF-8 data, causing mojibake. The Python scripts use `urllib.request` with proper `ensure_ascii=False` encoding - this is the correct and safe approach.

## Decision Guide

```
Get root folder?           → client.get_root_folder()
Browse folder contents?    → client.list_files(folder_token)
Get file details?          → client.get_file_meta(file_token, type)
Batch file metadata?       → client.batch_query_meta(request_docs)
Create folder?             → client.create_folder(name, folder_token)
Create online doc/sheet?   → client.create_file(folder_token, title, type)
Upload binary file ≤20MB?  → client.upload_file(file_name, parent_token, file_path, size)
Download binary file?      → client.download_file(file_token, save_path)
Copy file?                 → client.copy_file(file_token, name, type, folder_token)
Move file/folder?          → client.move_file(file_token, type, folder_token)
Delete file/folder?        → client.delete_file(file_token, type)
Search docs by keyword?    → client.search_files(query, docs_types)
Share file with user?      → client.add_permission(token, type, member_type, member_id, perm)
Change collaborator perm?  → client.update_permission(token, type, member_id, perm, member_type)
Revoke access?             → client.delete_permission(token, type, member_id, member_type)
Export doc/sheet to pdf?   → client.export_file(token, file_type, export_type) → poll get_export_result(ticket, token)
```

## API Methods (17 total)

### File (7)
| Method | Description |
|--------|-------------|
| `list_files(folder_token, page_size=200, ...)` | List folder contents; paginated, max 200/page |
| `get_file_meta(file_token, file_type)` | Get file metadata (name, url, parent) |
| `batch_query_meta(request_docs)` | Batch metadata for up to 200 files |
| `create_file(folder_token, title, file_type)` | Create online doc/sheet/mindnote/bitable |
| `copy_file(file_token, name, file_type, folder_token)` | Copy to another folder |
| `move_file(file_token, file_type, folder_token)` | Move; folder moves are async (task_id) |
| `delete_file(file_token, file_type)` | Delete to recycle bin; folder delete async |

### Upload / Download (4)
| Method | Description |
|--------|-------------|
| `get_root_folder()` | Get My Space root folder token |
| `create_folder(name, folder_token)` | Create new folder in parent |
| `upload_file(file_name, parent_token, file_path, size)` | Upload binary file (max 20 MB) |
| `download_file(file_token, save_path)` | Download binary file to local path |

### Permission / Search (4)
| Method | Description |
|--------|-------------|
| `search_files(query, docs_types, count, offset)` | Search user-accessible docs (user token only) |
| `add_permission(token, file_type, member_type, member_id, perm)` | Grant access |
| `update_permission(token, file_type, member_id, perm, member_type)` | Change role |
| `delete_permission(token, file_type, member_id, member_type)` | Revoke access |

### Export (2)
| Method | Description |
|--------|-------------|
| `export_file(file_token, file_type, export_type="pdf", sub_id=None)` | Start async export. `file_type`: doc/docx/sheet/bitable. `export_type`: pdf/docx (docs) or xlsx/csv (sheet/bitable). `sub_id` required for csv of a specific sheet. Returns `ticket` for polling. |
| `get_export_result(ticket, file_token)` | Poll export status by ticket. Returns `{job_status, file_token, file_name, ...}`. `job_status=0` = done; use returned `file_token` with `download_file()`. |

## Key Constraints

- **type param mandatory**: Pass correct file_type for all file ops — mismatched type fails silently
- **Upload max 20 MB**: Use multipart flow for larger files (not implemented here)
- **Download binary only**: doc/sheet/docx/bitable NOT downloadable via `download_file()` — use `export_file()` + `get_export_result()` instead
- **Async folder ops**: move/delete folders returns `task_id` — poll `/drive/v1/files/task_check`
- **Search user token only**: `search_files()` requires `user_access_token`
- **No concurrent folder writes**: Serialize ops to avoid error 1061045
- **Folder depth max 15 levels**: error 1062506; items per level max 1500: error 1062507

## Personnel Lookup

Use MCP tools directly - no Python needed:

**Find specific people:**
```
search_users(query="Huong") -> [{name, email, department, lark_open_id, ...}]
```

**Share with entire department** (e.g., "chia sẻ cho toàn bộ phòng Engineering"):
```
list_departments() -> [{department_id, name, ...}]
list_department_users(department_id) -> [{user_id, open_id, name, ...}]
```
Then call `add_permission` for each user's `open_id`.

Use `lark_open_id` as `member_id` for `add_permission` / `update_permission` / `delete_permission` with `member_type="openid"`.

## References

- [api-reference.md](./references/api-reference.md) — Full method params, return types, error codes
- [api-examples.md](./references/api-examples.md) — Code samples for common scenarios
- [api-validation.md](./references/api-validation.md) — File types, constraints, rate limits