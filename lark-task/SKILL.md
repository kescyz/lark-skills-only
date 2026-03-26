---
name: lark-task
description: LarkSuite task management - tasks, subtasks, tasklists, sections, custom fields. Use when user asks about tasks, todos, project tracking, or work items. Requires lark-token-manager MCP.
---

# Lark Task

Manage LarkSuite tasks, subtasks, tasklists, sections, and custom fields.

## Prerequisites

- `lark-token-manager` MCP server configured in `.mcp.json`
- `LARK_SKILL_API_KEY` exported before launching Claude Code
- Lark app with `task:task:read`, `task:task:write`, `task:tasklist:read`, `task:tasklist:write`, `task:section:read`, `task:section:write`, `task:custom_field:read`, `task:custom_field:write`, `task:comment:read`, `task:comment:write` scopes

## Initialization

### Step 1: Get user info from MCP

Call MCP `whoami` to get:
- `linked_users[].lark_open_id` -> user_open_id

### Step 2: Get access token from MCP

Call MCP `get_lark_token(app_name=LARK_APP_NAME)`
- If expired: MCP `refresh_lark_token` → if fails: MCP `start_oauth`

### Step 3: Initialize client

```python
import sys, os

# Find scripts path relative to SKILL.md location
skill_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(skill_dir, 'scripts'))

from lark_api import LarkTaskClient
from utils import datetime_to_task_timestamp, is_task_completed, get_today_range_ms

client = LarkTaskClient(
    access_token=TOKEN_FROM_MCP,
    user_open_id=OPEN_ID_FROM_WHOAMI
)
```

## Encoding (Non-ASCII Data)

ALWAYS use the Python scripts (`scripts/`) for ALL API calls. NEVER use `curl` in Bash for requests containing non-ASCII characters (Vietnamese, Chinese, Japanese, etc.). Windows terminal encoding (cp1252) corrupts UTF-8 data, causing mojibake. The Python scripts use `urllib.request` with proper `ensure_ascii=False` encoding - this is the correct and safe approach.

## API Methods

### Tasks
| Method | Description |
|--------|-------------|
| `list_tasks(completed=None)` | List "my_tasks" (owned tasks). `completed=False` for pending only, `True` for completed, `None` for all. Returns tasks in custom UI order. |
| `create_task(task_data)` | Create task. Auto-assigns to current user if no `members`. Requires `summary` (max 3000 chars). Supports `due` (ms timestamp), `members` (`[{id, type, role}]`), `reminders` (max 1, needs `due`), `tasklists`, `repeat_rule`, `client_token` for idempotency. Rate limit: 10/sec. |
| `get_task(guid)` | Get full task details including members, reminders, and custom field values. |
| `update_task(guid, data)` | Partial update using `{"task": {...}, "update_fields": ["field_name"]}` pattern. Only listed fields are changed. Manage members/reminders via separate APIs. |
| `delete_task(guid)` | Permanently delete task. Cannot be recovered. |

### Subtasks
| Method | Description |
|--------|-------------|
| `list_subtasks(task_guid)` | List all subtasks of a parent task. Returns same structure as tasks. |
| `create_subtask(task_guid, data)` | Create subtask under parent. Same fields as create_task; `summary` required. Requires edit permission on parent. Rate limit: 10/sec. |

### Tasklists
| Method | Description |
|--------|-------------|
| `list_tasklists()` | List all tasklists the user has access to. Returns `[{guid, name, members}]`. |
| `create_tasklist(name, members=None)` | Create tasklist. `name` required (max 100 chars). Creator becomes owner automatically. Add members as `[{id, type, role}]` with roles: `editor` or `viewer`. |
| `delete_tasklist(guid)` | Delete tasklist without deleting its tasks. |
| `get_tasklist_tasks(guid, completed=None)` | Get all tasks in a tasklist. Use `is_task_completed(t)` to check status. |

### Sections
| Method | Description |
|--------|-------------|
| `list_sections(resource_type, resource_id=None)` | List sections for `"tasklist"` (provide GUID) or `"my_tasks"`. Returns list with `guid`, `name`, `is_default` in UI order. |
| `create_section(name, resource_type, resource_id=None)` | Create section. `name` required (max 100 chars). Optional `insert_before`/`insert_after` for positioning (mutually exclusive). |
| `get_section(guid)` | Get section details. |
| `update_section(guid, name=None)` | Update section name. |
| `delete_section(guid)` | Delete section; tasks move to default section. |
| `list_section_tasks(guid, completed=None)` | List tasks within a section. |

### Collaboration
| Method | Description |
|--------|-------------|
| `add_task_comment(task_guid, content)` | Add a comment to a task. Returns created comment dict with `comment_id`. |
| `list_task_comments(task_guid)` | List all comments on a task (paginated). Returns list of comment dicts. |
| `add_task_reminder(task_guid, relative_fire_minute)` | Add reminder (minutes before due; 0 = at due time). Task must have due date; max 1 reminder. Returns reminder dict. |
| `add_task_dependency(task_guid, dependent_guid, dep_type="prev")` | Add dependency. `dep_type`: `prev` (this depends on dependent) or `next` (dependent depends on this). Returns all dependencies. |
| `remove_task_dependency(task_guid, dependent_guid)` | Remove a dependency by dependent task GUID. Returns `bool`. |
| `get_tasklist_details(tasklist_guid)` | Get full tasklist details including members, owner, and URL. Returns tasklist dict. |

### Custom Fields
| Method | Description |
|--------|-------------|
| `list_custom_fields(resource_type=None, resource_id=None)` | List custom fields for a resource. |
| `create_custom_field(name, type, resource_type, resource_id)` | Create and attach field to tasklist. `type`: `number`\|`member`\|`datetime`\|`single_select`\|`multi_select`\|`text`. Pass type-specific settings dict. Rate: 100/min. |
| `get_custom_field(guid)` | Get field details including options for select types. |
| `update_custom_field(guid, name=None, settings=None)` | Update field name or settings. |
| `add_custom_field_to_resource(guid, type, id)` | Link existing field to another tasklist. |
| `remove_custom_field_from_resource(guid, type, id)` | Unlink field from a tasklist. |

## Timestamp Rules

> **Task API** uses **MILLISECONDS** (13 digits): `"1704067200000"`

- `datetime_to_task_timestamp(dt)` -> milliseconds string
- `completed_at`: String `"0"` = not done, ms string = done

## Quick Examples

### Create task with deadline
```python
from datetime import datetime, timedelta
friday = (datetime.now() + timedelta(days=3)).replace(hour=17, minute=0, second=0, microsecond=0)
task = client.create_task({
    "summary": "Fix login bug",
    "due": {"timestamp": datetime_to_task_timestamp(friday), "is_all_day": False}
})
```

### Create workflow sections
```python
for name in ["Backlog", "In Progress", "Review", "Done"]:
    client.create_section(name=name, resource_type="tasklist", resource_id=tasklist_guid)
```

### Check progress
```python
all_tasks = client.get_tasklist_tasks(tasklist_guid)
done = [t for t in all_tasks if is_task_completed(t)]
print(f"Progress: {len(done)}/{len(all_tasks)} ({len(done)*100//len(all_tasks)}%)")
```

## Personnel Lookup

Use MCP tools directly - no Python needed:

**Find specific people:**
```
search_users(query="Huong") -> [{name, email, department, lark_open_id, ...}]
```

**List department members:**
```
list_departments() -> [{department_id, name, ...}]
list_department_users(department_id) -> [{user_id, name, ...}]
```

Use `lark_open_id` for Task members.

## References

- [api-reference.md](./references/api-reference.md) — Full method params, required/optional fields, return types
- [api-examples.md](./references/api-examples.md) — Code samples (kanban setup, custom fields, full workflow)
- [api-validation.md](./references/api-validation.md) — Member format, due format, custom field schemas, error codes
