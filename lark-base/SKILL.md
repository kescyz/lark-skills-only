---
name: lark-base
description: LarkSuite Bitable database management - tables, records, fields, views, permissions. Use when user asks about databases, Bitable, or data records. Requires lark-token-manager MCP.
---

# Lark Base

Manage Lark Bitable databases: create tables, define fields (26+ types), manage records (CRUD + batch), configure views, and set advanced permissions with custom roles.

## Prerequisites

- `lark-token-manager` MCP server configured
- `LARK_SKILL_API_KEY` exported before launching Claude Code
- Lark app scope: `bitable:app` (full CRUD)
- Optional: `contact:user.base:readonly`, `contact:user.employee_id:readonly` (user info in responses)

## Initialization

### Step 1: Get user info
Call MCP `whoami` → `linked_users[].lark_open_id` → user_open_id

### Step 2: Get token (prefer user token)
MCP `get_lark_token(app_name)` → ACCESS_TOKEN (user_access_token — preferred for traceability)
- If expired: MCP `refresh_lark_token` → if fails: MCP `start_oauth`
- Tenant token: only use when API requires it AND user is org admin (`whoami` → `is_admin: true` → `get_tenant_token`)

### Step 3: Init client
```python
import sys, os

# Find scripts path relative to SKILL.md location
skill_dir = os.path.dirname(os.path.abspath(__file__))
# Claude Code: scripts are at {project}/.claude/skills/lark-base/scripts/
# Adjust path based on your environment
sys.path.insert(0, os.path.join(skill_dir, 'scripts'))

from lark_api import LarkBaseClient
from utils import (FIELD_TEXT, FIELD_NUMBER, FIELD_SINGLE_SELECT, FIELD_DATE,
                   FIELD_DUPLEX_LINK, FIELD_BARCODE, build_select_options,
                   build_link_property, build_date_property, chunk_records)

client = LarkBaseClient(access_token=ACCESS_TOKEN, user_open_id=OPEN_ID)
```

## Encoding (Non-ASCII Data)

ALWAYS use the Python scripts (`scripts/`) for ALL API calls. NEVER use `curl` in Bash for requests containing non-ASCII characters (Vietnamese, Chinese, Japanese, etc.). Windows terminal encoding (cp1252) corrupts UTF-8 data, causing mojibake. The Python scripts use `urllib.request` with proper `ensure_ascii=False` encoding - this is the correct and safe approach.

## Decision Guide

```
Creating a new database?           → client.create_app(name)
Setting up tables with fields?     → client.create_table(app, name, fields)
Linking tables (ERD)?              → client.create_field(type=21, property=build_link_property(...))
Batch inserting data?              → client.batch_create_records(app, table, records)
Searching/filtering records?       → client.list_records(app, table, filter='...')
Setting up access control?         → client.update_app(is_advanced=True) → create_role → add_role_member
Managing views?                    → client.create_view(app, table, name, "kanban")
```

## API Methods (36 total)

### App (4)
| Method | Description |
|--------|-------------|
| `get_app(app_token)` | Get Base metadata (name, revision, is_advanced) |
| `create_app(name?, folder_token?)` | Create new Base (auto-creates 1 default table + 5 records) |
| `update_app(app_token, name?, is_advanced?)` | Update name, enable advanced permissions |
| `copy_app(app_token, name?, folder_token?, without_content?)` | Copy Base (structure only or with data) |

### Table (6)
| Method | Description |
|--------|-------------|
| `list_tables(app_token)` | List all tables (paginated) |
| `create_table(app_token, name, fields?)` | Create table with optional initial fields |
| `batch_create_tables(app_token, tables)` | Create multiple tables at once |
| `update_table(app_token, table_id, name)` | Rename table |
| `delete_table(app_token, table_id)` | Delete single table |
| `batch_delete_tables(app_token, table_ids)` | Delete up to 1000 tables |

### Field (4)
| Method | Description |
|--------|-------------|
| `list_fields(app_token, table_id)` | List all fields (max 300) |
| `create_field(app_token, table_id, field_name, field_type, ...)` | Create field (26+ types) |
| `update_field(app_token, table_id, field_id, field_name, field_type, ...)` | Full replace field |
| `delete_field(app_token, table_id, field_id)` | Delete field (cannot delete primary) |

### View (5)
| Method | Description |
|--------|-------------|
| `list_views(app_token, table_id)` | List views (max 200) |
| `get_view(app_token, table_id, view_id)` | Get view details |
| `create_view(app_token, table_id, view_name, view_type)` | Create: grid/kanban/gallery/gantt/form |
| `update_view(app_token, table_id, view_id, view_name)` | Rename view |
| `delete_view(app_token, table_id, view_id)` | Delete view (cannot delete last) |

### Record (8)
| Method | Description |
|--------|-------------|
| `list_records(app_token, table_id, filter?, sort?, ...)` | List/search with filter/sort (max 500/page) |
| `get_record(app_token, table_id, record_id)` | Get single record |
| `create_record(app_token, table_id, fields)` | Create single record |
| `batch_create_records(app_token, table_id, records, client_token?)` | Create up to 500 (all-or-nothing) |
| `update_record(app_token, table_id, record_id, fields)` | Update single record |
| `batch_update_records(app_token, table_id, records)` | Update up to 1000 |
| `delete_record(app_token, table_id, record_id)` | Delete single record |
| `batch_delete_records(app_token, table_id, record_ids)` | Delete up to 1000 |

### Permission (9)
| Method | Description |
|--------|-------------|
| `list_roles(app_token)` | List custom roles (max 30) |
| `create_role(app_token, role_name, table_roles?, block_roles?)` | Create role with permissions |
| `update_role(app_token, role_id, role_name, ...)` | Update role (full replace) |
| `delete_role(app_token, role_id)` | Delete role |
| `list_role_members(app_token, role_id)` | List collaborators in role |
| `add_role_member(app_token, role_id, member_id, member_type?)` | Add member |
| `delete_role_member(app_token, role_id, member_id)` | Remove member |
| `batch_add_role_members(app_token, role_id, member_list)` | Batch add (max 1000) |
| `batch_delete_role_members(app_token, role_id, member_ids)` | Batch remove (max 1000) |

## System Building Workflow

1. Gather requirements → user stories → features → KPIs
2. Design ERD with formula columns (think deeply about relationships)
3. **Create Base**: `create_app(name)` → delete default table after creating real tables
4. **Create tables with fields**: Use `create_table(name, fields)` or `batch_create_tables`
5. **Create relationships**: DuplexLink (type 21) for bidirectional links between tables
6. **Insert initial data**: `batch_create_records` (max 500/batch, use `chunk_records()`)
7. **Configure permissions**: `update_app(is_advanced=True)` → `create_role` → `add_role_member`
8. Suggest automation, dashboards, forms (human implements in Lark UI)

## Key Constraints

- **Default table quirk**: New Base auto-creates 1 table + 5 records. Create real tables first, delete default last.
- **Default primary field**: New table auto-creates a primary text field (Chinese name "多行文本"). Primary fields CANNOT be deleted — rename it to something useful instead (e.g., `update_field`).
- **`list_tables` returns flat list**: `list_tables()` uses `_fetch_all` → returns `[{table_id, name, ...}, ...]` directly (not `{"items": [...]}`). Access first table: `tables[0]`, not `tables["items"][0]`.
- **`build_select_options` returns property dict**: Returns `{"options": [...]}` — pass directly as `property` param in `create_field`.
- **Batch all-or-nothing**: One bad record kills entire batch. Validate before insert.
- **Single-write lock**: Only 1 concurrent write per table. Serialize writes.
- **Field update = full replace**: Must include ALL desired properties when updating.
- **Formula over Lookup**: Prefer Formula (type 20) for computed data from linked tables.
- **UI type fields** (Barcode, Currency, Progress, Rating): Use `FIELD_BARCODE` etc. — tuples of `(type, ui_type)`. Pass as `create_field(type=FIELD_BARCODE[0], ui_type=FIELD_BARCODE[1])`. Note: "Email" ui_type is **API-invalid** (error 99992402) - use plain `FIELD_TEXT` for email fields. Email ui_type can only be set via Lark UI.
- **`create_table` field limitations**: `ui_type` and Number `formatter` (e.g., `"0%"`) do NOT work in `create_table`'s initial `fields` array. Workaround: create table with basic fields first, then `update_field` to add `ui_type` or `property.formatter` after creation.

## Personnel Lookup

`MCP search_users(query="Name")` → `[{lark_open_id, ...}]` — use `lark_open_id` as `member_id` for `add_role_member` / `batch_add_role_members`.

**Folder Token**: `create_app(folder_token?)` — omit for "My Space" root; to get one activate `lark-drive` skill → `get_root_folder()`.

## References

- [api-reference.md](./references/api-reference.md) — Full method params, return types, error codes
- [api-examples.md](./references/api-examples.md) — Code samples for common scenarios
- [api-validation.md](./references/api-validation.md) — Field types, constraints, rate limits, error codes