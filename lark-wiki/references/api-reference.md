# Lark Wiki API Reference

> Token via `lark-token-manager` MCP. See [api-examples.md](./api-examples.md) for code samples. See [api-validation.md](./api-validation.md) for error codes and constraints.

## LarkWikiClient

```python
from lark_api import LarkWikiClient
client = LarkWikiClient(
    access_token="t-xxx",    # user_access_token or tenant_access_token
    user_open_id="ou_xxx",
)
```

---

## Space

### list_spaces(page_size=50, page_token=None)

List all Wiki spaces accessible to the token. Supports both token types.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| page_size | int | No | Max 50 (default 50) |
| page_token | str | No | Pagination cursor |

**Returns**: `{items: [...], has_more: bool, page_token: str?}`

Each item: `{space_id, name, description, space_type, visibility}`

---

### get_space(space_id)

Get space metadata.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| space_id | str | Yes | Space identifier |

**Returns**: `{space_id, name, description, space_type, visibility, ...}`

---

### create_space(name=None, description=None)

Create a new Wiki space. **Requires user_access_token.**

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| name | str | No | Space display name |
| description | str | No | Space description |

**Returns**: `{space_id, name, description, space_type}`

---

### update_space_setting(space_id, create_setting=None, security_setting=None, comment_setting=None)

Update space settings. Admin only.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| space_id | str | Yes | Target space |
| create_setting | str | No | `"allow"` or `"not_allow"` — who can create pages |
| security_setting | str | No | `"allow"` or `"not_allow"` — external share |
| comment_setting | str | No | `"allow"` or `"not_allow"` — comments |

**Returns**: `{setting}` with updated values.

---

## Node

### create_node(space_id, obj_type, parent_node_token=None, title=None, node_type="origin")

Create a new page/node in a Wiki space.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| space_id | str | Yes | Target space |
| obj_type | str | Yes | `"doc"`, `"docx"`, `"sheet"`, `"bitable"`, `"mindnote"`, `"file"` |
| parent_node_token | str | No | Parent node. `None` = root level |
| title | str | No | Page title. Defaults to empty |
| node_type | str | No | `"origin"` (real) or `"shortcut"` (alias). Default: `"origin"` |

**Returns**: `{node_token, obj_token, title, obj_type, node_type, space_id, parent_node_token, ...}`

---

### get_node(token)

Get node metadata by token. **CRITICAL: uses `?token=` query param, not path param.**

Endpoint: `GET /wiki/v2/spaces/get_node?token=...`

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| token | str | Yes | Node token (wiki_token) |

**Returns**: `{node_token, obj_token, title, obj_type, parent_node_token, space_id, ...}`

---

### list_nodes(space_id, parent_node_token=None, page_size=50, page_token=None)

List child nodes in a space. Same URL as create_node but GET method.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| space_id | str | Yes | Target space |
| parent_node_token | str | No | List children of this node. `None` = root children |
| page_size | int | No | Max 50 (default 50) |
| page_token | str | No | Pagination cursor |

**Returns**: `{items: [...], has_more: bool, page_token: str?}`

---

### move_node(space_id, node_token, target_parent_token=None, target_space_id=None)

Move a node to a new parent or different space. Cross-space supported.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| space_id | str | Yes | Source space |
| node_token | str | Yes | Node to move |
| target_parent_token | str | No | New parent node. `None` = root |
| target_space_id | str | No | New space. `None` = same space |

**Returns**: `{node}` with updated location.

---

### copy_node(space_id, node_token, target_parent_token=None, target_space_id=None, title=None)

Copy a node to a new location.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| space_id | str | Yes | Source space |
| node_token | str | Yes | Node to copy |
| target_parent_token | str | No | Target parent. `None` = root |
| target_space_id | str | No | Target space. `None` = same space |
| title | str | No | New title. `None` = keep original |

**Returns**: `{node}` for the new copy.

---

### update_title(space_id, node_token, title)

Rename a node. **Only works for doc, docx, shortcut. NOT sheet/bitable/mindnote/file.**

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| space_id | str | Yes | Space identifier |
| node_token | str | Yes | Node to rename |
| title | str | Yes | New title string |

**Returns**: `{}` on success.

---

## Member + Search + Task

### add_member(space_id, member_type, member_id, member_role, need_notification=False)

Add a member to a Wiki space.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| space_id | str | Yes | Target space |
| member_type | str | Yes | `"userid"`, `"openid"`, `"unionid"`, `"email"`, `"departmentid"`, `"openchatid"` |
| member_id | str | Yes | Member identifier |
| member_role | str | Yes | `"admin"` or `"member"` |
| need_notification | bool | No | Notify member. Default `False` |

**Returns**: `{member_id, member_type, member_role}`

**Note**: Public space → admin role only. Personal space → member role only (error 131101 otherwise).

---

### delete_member(space_id, member_id, member_type, member_role)

Remove a member. **CRITICAL: sends JSON body in DELETE request.**

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| space_id | str | Yes | Target space |
| member_id | str | Yes | Member to remove |
| member_type | str | Yes | Same type used when adding |
| member_role | str | Yes | `"admin"` or `"member"` |

**Returns**: `{}` on success.

---

### search_wiki(query, space_id=None, node_id=None, page_size=20, page_token=None)

Full-text search across Wiki. **Requires user_access_token.**

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| query | str | Yes | Search keywords |
| space_id | str | No | Limit to space. `None` = all spaces |
| node_id | str | No | Limit to node subtree |
| page_size | int | No | Max 50 (default 20) |
| page_token | str | No | Pagination cursor |

**Returns**: `{items: [...], has_more: bool, page_token: str?}`

---

### move_docs_to_wiki(space_id, obj_type, obj_token, parent_wiki_token=None)

Migrate a Lark document into Wiki. Async — may return task_id or wiki_token.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| space_id | str | Yes | Target Wiki space |
| obj_type | str | Yes | `"doc"`, `"docx"`, `"sheet"`, `"bitable"`, `"mindnote"`, `"file"` |
| obj_token | str | Yes | Document token to migrate |
| parent_wiki_token | str | No | Target parent node. `None` = root |

**Returns**: `{wiki_token?: str, task_id?: str}`
- `wiki_token` present → migration complete immediately
- `task_id` present → async, poll with `get_task(task_id)`

---

### get_task(task_id, task_type="move")

Poll status of an async Wiki task. Creator-only.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| task_id | str | Yes | Task identifier from move_docs_to_wiki |
| task_type | str | No | Currently only `"move"`. Default `"move"` |

**Returns**: `{task_id, task_type, status, ...}`
- `status`: `"pending"`, `"done"`, `"failed"`
