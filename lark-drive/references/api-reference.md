# Lark Drive API Reference

Full parameter reference for all 15 methods in `LarkDriveClient`.

---

## File Methods (`lark_api_file.py`)

### `list_files(folder_token, page_size=200, page_token=None, order_by="EditedTime", direction="DESC")`

**GET** `/drive/v1/files`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| folder_token | str | Yes | Target folder token (prefix: `fld`) |
| page_size | int | No | Items per page, max 200 (default 200) |
| page_token | str | No | Pagination cursor from previous response |
| order_by | str | No | `EditedTime` (default), `CreatedTime`, `Name` |
| direction | str | No | `ASC` or `DESC` (default DESC) |

**Returns:** `{files: [{name, token, type, parent_token, url, shortcut_info?}], next_page_token, has_more}`

---

### `get_file_meta(file_token, file_type)`

**GET** `/drive/v1/files/:file_token?type=<file_type>`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| file_token | str | Yes | File token |
| file_type | str | Yes | doc, docx, sheet, bitable, mindnote, file, folder |

**Returns:** `{name, token, type, parent_token, url, owner_id, ...}`

---

### `batch_query_meta(request_docs, with_url=False, user_id_type="open_id")`

**POST** `/drive/v1/metas/batch_query`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| request_docs | list | Yes | `[{doc_token, doc_type}]`, max 200 items |
| with_url | bool | No | Include access URL (default False) |
| user_id_type | str | No | `open_id` (default), `union_id`, `user_id` |

**Returns:** `{metas: [{title, owner_id, create_time, latest_modify_user, latest_modify_time, url?}], failed_list: [{token, error}]}`

**Error codes in failed_list:** 970002=unsupported type, 970003=no permission, 970005=not found

---

### `create_file(folder_token, title, file_type)`

**POST** `/drive/explorer/v2/file/:folderToken`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| folder_token | str | Yes | Parent folder token |
| title | str | Yes | Document title |
| file_type | str | Yes | doc, docx, sheet, mindnote, bitable |

**Returns:** `{url, token, type}`

---

### `copy_file(file_token, name, file_type, folder_token)`

**POST** `/drive/v1/files/:file_token/copy`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| file_token | str | Yes | Source file token |
| name | str | Yes | New file name (not auto-generated) |
| file_type | str | Yes | Type of source file |
| folder_token | str | Yes | Destination folder token |

**Returns:** `{file: {token, name, type, parent_token, url}}`

---

### `move_file(file_token, file_type, folder_token)`

**POST** `/drive/v1/files/:file_token/move`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| file_token | str | Yes | File/folder token to move |
| file_type | str | Yes | Type of item being moved |
| folder_token | str | Yes | Destination folder token |

**Returns:** `{}` for files, `{task_id: str}` for folder moves (async — poll task_check)

---

### `delete_file(file_token, file_type)`

**DELETE** `/drive/v1/files/:file_token?type=<file_type>`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| file_token | str | Yes | File/folder token to delete |
| file_type | str | Yes | Type of item (required query param) |

**Returns:** `{}` for files, `{task_id: str}` for folder deletes (async)

---

## Upload/Download Methods (`lark_api_upload_download.py`)

### `get_root_folder()`

**GET** `/drive/explorer/v2/root_folder/meta`

No parameters.

**Returns:** `{token: str, id: str}` — `token` is the root `folder_token` for My Space

---

### `create_folder(name, folder_token)`

**POST** `/drive/v1/files/create_folder`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| name | str | Yes | Folder name (max 250 chars) |
| folder_token | str | Yes | Parent folder token |

**Returns:** `{token: str, id: str}`

---

### `upload_file(file_name, parent_token, file_path, size)`

**POST** `/drive/v1/files/upload_all` (multipart/form-data via curl)

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| file_name | str | Yes | Name to save as in Drive (max 250 chars) |
| parent_token | str | Yes | Destination folder token |
| file_path | str | Yes | Absolute local path to file |
| size | int | Yes | File size in bytes (max 20971520 = 20 MB) |

**Returns:** `{file_token: str}`

**Errors:** ValueError if file missing or >20 MB; Exception on API error

---

### `download_file(file_token, save_path)`

**GET** `/drive/v1/files/:file_token/download` (binary stream via curl -o)

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| file_token | str | Yes | File token (prefix: `box`) |
| save_path | str | Yes | Absolute local path to write |

**Returns:** `save_path` string on success

**Note:** Only works for uploaded binary files. Online docs (doc/sheet/docx/bitable) NOT supported.

---

## Permission/Search Methods (`lark_api_permission.py`)

### `search_files(query, docs_types=None, count=50, offset=0)`

**POST** `/suite/docs-api/search/object`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| query | str | Yes | Search keyword |
| docs_types | list | No | Filter: doc, sheet, slide, bitable, mindnote, file |
| count | int | No | Results per page (max 50, default 50) |
| offset | int | No | Pagination offset (offset + count < 200) |

**Returns:** `{docs_entities: [{token, type, title, owner_id}], total, has_more}`

**Requires:** user_access_token only — tenant token returns empty results

---

### `add_permission(token, file_type, member_type, member_id, perm, need_notification=False)`

**POST** `/drive/v1/permissions/:token/members?type=<file_type>`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| token | str | Yes | File/doc token |
| file_type | str | Yes | doc, sheet, file, wiki, bitable, docx |
| member_type | str | Yes | email, openid, openchat, opendepartmentid, userid |
| member_id | str | Yes | User/group identifier |
| perm | str | Yes | view, edit, or full_access |
| need_notification | bool | No | Send email (user_access_token only) |

**Returns:** `{member: {member_type, member_id, perm, ...}}`

---

### `update_permission(token, file_type, member_id, perm, member_type)`

**PUT** `/drive/v1/permissions/:token/members/:member_id?type=<file_type>`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| token | str | Yes | File/doc token |
| file_type | str | Yes | doc, sheet, file, wiki, bitable, docx |
| member_id | str | Yes | User/group identifier |
| perm | str | Yes | New permission: view, edit, full_access |
| member_type | str | Yes | email, openid, openchat, opendepartmentid, userid |

**Returns:** `{member: {member_type, member_id, perm}}`

---

### `delete_permission(token, file_type, member_id, member_type)`

**DELETE** `/drive/v1/permissions/:token/members/:member_id?type=<file_type>&member_type=<member_type>`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| token | str | Yes | File/doc token |
| file_type | str | Yes | doc, sheet, file, wiki, bitable, docx |
| member_id | str | Yes | User/group identifier to revoke |
| member_type | str | Yes | email, openid, openchat, opendepartmentid, userid |

**Returns:** `{}` on success

---

## Async Task Polling

For folder move/delete, response contains `task_id`. Poll to check completion:

**GET** `/drive/v1/files/task_check?task_id=<task_id>`

**Returns:** `{job_status: 0}` when complete (0=done, 1-6=processing)
