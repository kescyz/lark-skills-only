---
name: lark-wiki
description: LarkSuite Wiki knowledge base management - spaces, nodes, pages, members, search. Use when user asks about wiki, knowledge base, or internal docs. Requires lark-token-manager MCP.
---

# Lark Wiki

Manage Lark Wiki knowledge bases: browse and create spaces, create/move/copy nodes (pages),
manage space members, search content, and migrate Lark docs into Wiki.

## Prerequisites

- `lark-token-manager` MCP server configured
- `LARK_SKILL_API_KEY` exported before launching Claude Code
- Lark app scopes: `wiki:wiki` (read+write), `wiki:wiki:readonly` (read only)
- Note: `create_space` and `search_wiki` require user_access_token

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

from lark_api import LarkWikiClient
from utils import OBJ_TYPE_DOCX, NODE_TYPE_ORIGIN, MEMBER_ROLE_ADMIN

client = LarkWikiClient(access_token=ACCESS_TOKEN, user_open_id=OPEN_ID)
```

## Encoding (Non-ASCII Data)

ALWAYS use the Python scripts (`scripts/`) for ALL API calls. NEVER use `curl` in Bash for requests containing non-ASCII characters (Vietnamese, Chinese, Japanese, etc.). Windows terminal encoding (cp1252) corrupts UTF-8 data, causing mojibake. The Python scripts use `urllib.request` with proper `ensure_ascii=False` encoding - this is the correct and safe approach.

## Decision Guide

```
List all spaces?                   → client.list_spaces()
Get space details?                 → client.get_space(space_id)
Create new space?                  → client.create_space(name) [user_access_token only]
Change space settings?             → client.update_space_setting(space_id, ...)

Create a new page?                 → client.create_node(space_id, obj_type="docx")
Get page info?                     → client.get_node(token)  [query param, not path!]
List pages (children)?             → client.list_nodes(space_id, parent_node_token)
Move page to new location?         → client.move_node(space_id, node_token, target_parent_token)
Copy page?                         → client.copy_node(space_id, node_token, ...)
Rename a doc/docx page?            → client.update_title(space_id, node_token, title)

Add member to space?               → client.add_member(space_id, member_type, member_id, role)
Remove member from space?          → client.delete_member(space_id, member_id, type, role)
Search Wiki content?               → client.search_wiki(query) [user_access_token only]
Move existing doc into Wiki?       → client.move_docs_to_wiki(space_id, obj_type, obj_token)
Check async task status?           → client.get_task(task_id)
```

## API Methods (15 total)

### Space (4)
| Method | Description |
|--------|-------------|
| `list_spaces(page_size=50, page_token=None)` | List accessible spaces (max 50/page) |
| `get_space(space_id)` | Get space metadata |
| `create_space(name=None, description=None)` | Create space — user_access_token only |
| `update_space_setting(space_id, create_setting?, security_setting?, comment_setting?)` | Update space settings (admin only) |

### Node (6)
| Method | Description |
|--------|-------------|
| `create_node(space_id, obj_type, parent_node_token=None, title=None, node_type="origin")` | Create page at root or under parent |
| `get_node(token)` | Get node by token — query param `?token=` |
| `list_nodes(space_id, parent_node_token=None, page_size=50, page_token=None)` | List child nodes |
| `move_node(space_id, node_token, target_parent_token=None, target_space_id=None)` | Move node (cross-space OK) |
| `copy_node(space_id, node_token, target_parent_token=None, target_space_id=None, title=None)` | Copy node |
| `update_title(space_id, node_token, title)` | Rename — doc/docx/shortcut only |

### Member + Search + Task (5)
| Method | Description |
|--------|-------------|
| `add_member(space_id, member_type, member_id, member_role, need_notification=False)` | Add space member |
| `delete_member(space_id, member_id, member_type, member_role)` | Remove member (body required in DELETE) |
| `search_wiki(query, space_id=None, node_id=None, page_size=20, page_token=None)` | Full-text search — user_access_token only |
| `move_docs_to_wiki(space_id, obj_type, obj_token, parent_wiki_token=None)` | Migrate doc to Wiki (async) |
| `get_task(task_id, task_type="move")` | Poll async task status |

## Key Constraints

- **NO delete node API** — Wiki nodes cannot be deleted via API. Use Lark UI instead.
- **`get_node` uses query param**: `GET /wiki/v2/spaces/get_node?token=X` (not path param)
- **`delete_member` needs body**: Send `member_type` + `member_role` as JSON body in DELETE
- **`update_title` limited**: Only doc, docx, shortcut — NOT sheet, bitable, mindnote, file
- **`create_space` + `search_wiki`**: user_access_token required (tenant token fails)
- **Public space**: add/remove admins only (error 131101 if using member role)
- **Personal space**: add/remove members only (error 131101 if using admin role)
- **`move_docs_to_wiki` async**: check response for `wiki_token` (done) or `task_id` (poll needed)
- **`items` can be null**: always handled with `or []` in list responses
- **Limits**: 400k nodes/space, 50 depth levels, 2000 children per parent, page_size max 50

## Personnel Lookup

Use MCP tools directly - no Python needed:

**Find specific people:**
```
search_users(query="Huong") -> [{name, email, department, lark_open_id, ...}]
```

**Add entire department to wiki space:**
```
list_departments() -> [{department_id, name, ...}]
list_department_users(department_id) -> [{user_id, open_id, name, ...}]
```
Then use each `open_id` as `member_id` for `add_member` with `member_type="openid"`.

## Cross-Domain Operations

**Editing docx node content**: Wiki nodes created with `obj_type="docx"` produce an empty document. To add content, use DocX API block operations with the node's `obj_token` as `document_id`. Activate `lark-docs` skill for this.

**Deleting nodes**: No delete node API exists. Nodes must be deleted via Lark UI. For Drive-backed nodes (obj_type=file/sheet), you can delete via Drive API: `DELETE /open-apis/drive/v1/files/:obj_token?type=<file_type>`.

## References

- [api-reference.md](./references/api-reference.md) — Full method params, return types
- [api-examples.md](./references/api-examples.md) — Code samples for common scenarios
- [api-validation.md](./references/api-validation.md) — Error codes, constraints, rate limits