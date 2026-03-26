# Lark Drive API Validation Reference

Constraints, file types, error codes, and rate limits.

---

## File Type Enums

| Constant | Value | Notes |
|----------|-------|-------|
| `FILE_TYPE_DOC` | `"doc"` | Legacy Lark Doc |
| `FILE_TYPE_DOCX` | `"docx"` | New Lark Doc |
| `FILE_TYPE_SHEET` | `"sheet"` | Lark Sheet |
| `FILE_TYPE_MINDNOTE` | `"mindnote"` | Mind map |
| `FILE_TYPE_BITABLE` | `"bitable"` | Lark Base |
| `FILE_TYPE_FILE` | `"file"` | Uploaded binary file |
| `FILE_TYPE_FOLDER` | `"folder"` | Folder |
| `FILE_TYPE_WIKI` | `"wiki"` | Wiki node |

**Creatable via `create_file()`:** doc, docx, sheet, mindnote, bitable

**Downloadable via `download_file()`:** file only (prefix: `box*`)

---

## Token Prefixes

| Token Type | Prefix | Example |
|------------|--------|---------|
| Folder | `fld` | `fldABCxyz123` |
| Uploaded file | `box` | `boxABCxyz123` |
| Doc (legacy) | `doc` | `docABCxyz123` |
| Sheet | `sht` | `shtABCxyz123` |
| Bitable | `app` | `appABCxyz123` |
| Docx (new) | varies | — |
| Shortcut/Node | `nod` | `nodABCxyz123` |

---

## Permission Values

| Value | Description |
|-------|-------------|
| `view` | Read-only access |
| `edit` | Read and write access |
| `full_access` | Full control including sharing |

---

## Member Types

| Value | Description |
|-------|-------------|
| `email` | User email address |
| `openid` | Lark open_id (prefix: `ou_`) |
| `openchat` | Group chat ID |
| `opendepartmentid` | Department ID |
| `userid` | Employee user ID |

---

## Size & Structural Limits

| Constraint | Limit | Error Code |
|------------|-------|------------|
| Single file upload | 20 MB (20,971,520 bytes) | 1061043 |
| File/folder name | 250 characters | — |
| Items per folder level | 1,500 | 1062507 |
| Folder depth | 15 levels | 1062506 |
| Tree size | 400,000 nodes | 1062505 |
| Batch meta query | 200 files | ValueError |
| Search count per page | 50 | — |
| Search offset + count | < 200 | — |

---

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Write ops (copy/move/delete/create/upload) | 5 QPS |
| Metadata query | 50 QPS, 1,000/min |
| Import/Export | 100/min |
| No concurrency | Folder-level writes must be serialized |

---

## Error Codes

### Upload Errors
| Code | Meaning | Action |
|------|---------|--------|
| 1061043 | File > 20 MB | Use multipart upload |
| 1061101 | Tenant quota exceeded | Free up space |
| 1061061 | User quota exceeded | Free up space |
| 1061045 | Resource contention | Retry with backoff |
| 1061021 | Transaction expired (5 min) | Re-upload file |

### Folder/Structure Errors
| Code | Meaning | Action |
|------|---------|--------|
| 1062507 | Folder item limit (1500) | Create sub-folder |
| 1062506 | Folder depth limit (15) | Flatten hierarchy |
| 1062505 | Tree size limit (400k) | Clean up files |

### Permission / Meta Errors
| Code | Meaning | Action |
|------|---------|--------|
| 970002 | Unsupported doc type | Check doc_type value |
| 970003 | No permission | Request access or check token |
| 970005 | File not found | Verify token and type |

### General Errors
| Code | Meaning | Action |
|------|---------|--------|
| 1254290 | Rate limit hit | Retry with exponential backoff |
| 99991663 | Token expired | Refresh via MCP `get_lark_token` |
| 99991664 | Token invalid | Re-authenticate |

---

## Async Task Status (`task_check` job_status)

| Status | Meaning |
|--------|---------|
| 0 | Complete |
| 1 | Initializing |
| 2 | Processing |
| 3 | Error |
| 4-6 | Various processing states |

Poll endpoint: `GET /drive/v1/files/task_check?task_id=<id>`
Recommended interval: start at 1s, cap at 30s with exponential backoff.

---

## Token Type Requirements

| Method | tenant_access_token | user_access_token |
|--------|--------------------|--------------------|
| list_files | Yes | Yes |
| upload_file | Yes | Yes |
| download_file | Yes | Yes |
| create_file | Yes | Yes |
| copy/move/delete | Yes | Yes |
| search_files | **No** | **Required** |
| add/update/delete_permission | Yes | Yes |
| need_notification (add_permission) | No | Required |
