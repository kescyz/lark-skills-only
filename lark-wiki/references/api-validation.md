# Lark Wiki API Validation

> Constraints, error codes, rate limits. See [api-reference.md](./api-reference.md) for params. See [api-examples.md](./api-examples.md) for code samples.

## Capacity Limits

| Resource | Limit |
|----------|-------|
| Nodes per space | 400,000 |
| Tree depth | 50 levels |
| Children per parent node | 2,000 |
| `page_size` max | 50 |
| `search_wiki` page_size max | 50 |

## Token Type Requirements

| Method | Token Type |
|--------|-----------|
| `list_spaces` | user or tenant |
| `get_space` | user or tenant |
| `create_space` | **user_access_token only** |
| `update_space_setting` | user or tenant (admin) |
| `create_node` | user or tenant |
| `get_node` | user or tenant |
| `list_nodes` | user or tenant |
| `move_node` | user or tenant |
| `copy_node` | user or tenant |
| `update_title` | user or tenant |
| `add_member` | user or tenant (admin) |
| `delete_member` | user or tenant (admin) |
| `search_wiki` | **user_access_token only** |
| `move_docs_to_wiki` | user or tenant |
| `get_task` | user or tenant (creator only) |

## Object Types (`obj_type`)

| Value | Document Type | Supports `update_title` |
|-------|--------------|------------------------|
| `"doc"` | Legacy Doc | Yes |
| `"docx"` | New Doc | Yes |
| `"sheet"` | Spreadsheet | No |
| `"bitable"` | Base (database) | No |
| `"mindnote"` | Mind map | No |
| `"file"` | File attachment | No |

**Note**: Shortcuts (`node_type="shortcut"`) also support `update_title`.

## Member Type Values (`member_type`)

| Value | Description |
|-------|-------------|
| `"userid"` | Lark user ID |
| `"openid"` | Open ID (`ou_xxx`) |
| `"unionid"` | Union ID |
| `"email"` | Email address |
| `"departmentid"` | Department ID |
| `"openchatid"` | Group chat ID |

## Space Type vs Member Role

| Space Type | Allowed Role | Error if Wrong Role |
|------------|-------------|---------------------|
| Public (`"team"`) | `"admin"` only | 131101 |
| Personal | `"member"` only | 131101 |

## Space Setting Values

| Field | Values | Default |
|-------|--------|---------|
| `create_setting` | `"allow"`, `"not_allow"` | `"allow"` |
| `security_setting` | `"allow"`, `"not_allow"` | `"not_allow"` |
| `comment_setting` | `"allow"`, `"not_allow"` | `"allow"` |

## Async Task Status (`get_task`)

| Status | Meaning |
|--------|---------|
| `"pending"` | Still processing — continue polling |
| `"done"` | Migration complete — check for `wiki_token` in result |
| `"failed"` | Migration failed — check error info |

## Error Codes

| Code | Meaning | Fix |
|------|---------|-----|
| 131101 | Wrong member role for space type | Use `admin` for public, `member` for personal |
| 1254290 | Rate limit exceeded | Retry with exponential backoff (handled by base client) |
| 1254003 | Permission denied | Check token type and app scopes |
| 1254036 | Node not found | Verify token is correct and accessible |
| 1254100 | Space not found | Verify space_id |
| 1254401 | `update_title` unsupported type | Only doc/docx/shortcut supported |

## Required App Scopes

| Scope | Access Level |
|-------|-------------|
| `wiki:wiki` | Full read + write access |
| `wiki:wiki:readonly` | Read-only access |

## API Quirks (Implementation Notes)

1. **`get_node` URL**: `GET /wiki/v2/spaces/get_node?token=X` — query param, NOT path param
2. **`delete_member` body**: DELETE method requires JSON body with `member_type` + `member_role`
3. **`items` null safety**: List endpoints return `null` for empty `items` — always use `or []`
4. **`data` null safety**: Empty responses return `"data": null` — always use `or {}`
5. **No delete node API**: Wiki nodes cannot be deleted via API (Lark limitation) — use UI
6. **`move_docs_to_wiki` dual response**: Returns `wiki_token` (immediate) OR `task_id` (async)
7. **Task creator only**: `get_task` only works for the user who initiated the migration
