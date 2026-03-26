# Lark Task API Reference

> Token management handled by `lark-token-manager` MCP server.
> See [api-examples.md](./api-examples.md) for code samples.
> See [api-validation.md](./api-validation.md) for full enums, schemas, error codes.

## LarkTaskClient

```python
from lark_api import LarkTaskClient
client = LarkTaskClient(access_token="u-xxx", user_open_id="ou_xxx")
```

---

## Tasks

### list_tasks(completed=None)

List all tasks owned by the authenticated user ("my_tasks"). Returns tasks in custom UI order. Pagination is handled internally.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| completed | bool | No | Filter by completion status | `True` = completed only, `False` = pending only, `None` = all |

**Returns**: `List[Dict]` — task objects
**Errors**: 1470400 (bad params), 1470500 (server error)

---

### create_task(task_data)

Create a new task. Auto-assigns to the authenticated user if no `members` are specified. Rate-limited to 10/sec.

**Params (task_data)**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| summary | string | **Yes** | Task title | max 3000 chars; cannot be empty |
| description | string | No | Task description | max 3000 chars |
| due | due_object | No | Deadline | `{"timestamp": "ms_string", "is_all_day": bool}` |
| members | member[] | No | Assignees/followers | See member format below; max 50 per request |
| start | start_object | No | Start time | Same format as `due` |
| reminders | reminder[] | No | Deadline reminders | Max 1 reminder; requires `due` to be set |
| tasklists | task_in_tasklist_info[] | No | Add to tasklist(s) at creation | Requires edit permission on each tasklist |
| client_token | string | No | Idempotency key | 10-100 chars; prevents duplicate creation |
| repeat_rule | string | No | Recurring task rule | RRULE subset per RFC 5545; requires `due` |
| completed_at | string | No | Create as completed | ms timestamp string; `"0"` = not completed |
| mode | int | No | Completion mode | `1`=all-sign (all must complete), `2`=any-sign (default) |
| is_milestone | bool | No | Mark as milestone | default: `false` |
| custom_fields | input_custom_field_value[] | No | Set custom field values | Field must be associated with target tasklist |

**Member format**:
```python
{"id": "ou_xxx", "type": "user", "role": "assignee"}
# role: "assignee" | "follower"
# type: "user" (only supported type currently)
```

**due / start format**:
```python
{"timestamp": "1704355200000", "is_all_day": False}  # specific time
{"timestamp": "1704355200000", "is_all_day": True}   # all-day date
```

**Returns**: `Dict` — created task with `guid`
**Errors**: 1470400 (missing summary, no due for reminder), 1470403 (no tasklist permission), 1470404 (tasklist not found)

---

### get_task(task_guid)

Get full details of a single task including members, custom fields, reminders, and tasklist membership.

**Params**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_guid | string | **Yes** | Task GUID from create/list |

**Returns**: `Dict` — full task object
**Errors**: 1470404 (not found/deleted), 1470403 (no read permission)

---

### update_task(task_guid, data)

Partial update using `{task: {...}, update_fields: [...]}` pattern. Only fields listed in `update_fields` are modified; others are unchanged.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| task_guid | string | **Yes** | Task GUID | — |
| task | dict | No | Fields to update | Only fields in `update_fields` are applied |
| update_fields | string[] | **Yes** | Field names to update | See updatable fields below |

**Updatable fields** (put in update_fields list):
- `"summary"` — task title
- `"description"` — task description
- `"due"` — deadline
- `"start"` — start time
- `"completed_at"` — complete/uncomplete (`"0"` = uncomplete)
- `"repeat_rule"` — recurrence rule (cannot update with `completed_at`)
- `"mode"` — completion mode
- `"is_milestone"` — milestone flag
- `"extra"` — custom attached data

**Note**: Members, reminders, and tasklist membership are managed by separate add/remove APIs.

**Returns**: `Dict` — updated task object
**Errors**: 1470400 (bad params, empty summary, completed task re-completion), 1470403 (no edit permission), 1470404 (not found)

---

### delete_task(task_guid)

Permanently delete a task. Deleted tasks cannot be recovered.

**Params**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_guid | string | **Yes** | Task GUID |

**Returns**: `bool` — `True` on success
**Errors**: 1470403 (no permission), 1470404 (not found)

---

## Subtasks

### list_subtasks(task_guid)

List all subtasks of a parent task.

**Params**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_guid | string | **Yes** | Parent task GUID |

**Returns**: `List[Dict]` — subtask objects (same structure as tasks)
**Errors**: 1470404 (parent not found), 1470403 (no read permission)

---

### create_subtask(task_guid, data, parent_members=None)

Create a subtask under a parent task. Same fields as `create_task`. If no members specified and `parent_members` provided, inherits parent's assignees.

**Params**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_guid | string | **Yes** | Parent task GUID |
| data | dict | **Yes** | Same fields as create_task; `summary` required |
| parent_members | list | No | Pass parent task's members to inherit assignees |

**Returns**: `Dict` — created subtask with `guid`
**Errors**: 1470400 (bad params), 1470403 (no edit permission on parent), 1470404 (parent not found)

---

## Tasklists

### list_tasklists()

List all tasklists the authenticated user has access to.

**Returns**: `List[Dict]` — tasklist objects with `guid`, `name`, `members`
**Errors**: 1470500 (server error)

---

### create_tasklist(name, members=None)

Create a new tasklist. Creator automatically becomes owner.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| name | string | **Yes** | Tasklist name | max 100 chars; cannot be empty |
| members | member[] | No | Initial member list | max 500; use `open_id` for user `id` |

**Returns**: `Dict` — created tasklist with `guid`
**Errors**: 1470400 (empty name), 1470500 (server error)

---

### delete_tasklist(guid)

Delete a tasklist. Does not delete tasks within it.

**Params**: `guid` (string, required)
**Returns**: `bool`
**Errors**: 1470403 (no permission), 1470404 (not found)

---

### get_tasklist_tasks(guid, completed=None)

Get all tasks belonging to a tasklist.

**Params**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| guid | string | **Yes** | Tasklist GUID |
| completed | bool | No | Filter by completion (`None` = all) |

**Returns**: `List[Dict]` — task objects
**Errors**: 1470403 (no read permission), 1470404 (not found)

---

## Sections

### list_sections(resource_type, resource_id=None)

List sections for a tasklist or "my_tasks". Returns list in UI display order.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| resource_type | string | **Yes** | `"tasklist"` or `"my_tasks"` | — |
| resource_id | string | No | Tasklist GUID — required when resource_type=`"tasklist"` | — |

**Returns**: `List[Dict]` — section objects with `guid`, `name`, `is_default`
**Errors**: 1470403 (no permission), 1470404 (resource not found)

---

### create_section(name, resource_type, resource_id=None, insert_before=None, insert_after=None)

Create a section in a tasklist or "my_tasks". New section placed at end by default.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| name | string | **Yes** | Section name | max 100 chars |
| resource_type | string | **Yes** | `"tasklist"` or `"my_tasks"` | — |
| resource_id | string | No | Tasklist GUID (required for `"tasklist"` type) | — |
| insert_before | string | No | Place new section before this section GUID | Mutually exclusive with insert_after |
| insert_after | string | No | Place new section after this section GUID | Mutually exclusive with insert_before |

**Returns**: `Dict` — created section with `guid`, `name`, `is_default`
**Errors**: 1470400 (both insert_before and insert_after set), 1470403 (no permission), 1470404 (resource not found)

---

### get_section(guid)

Get details of a single section.

**Params**: `guid` (string, required)
**Returns**: `Dict` — section object
**Errors**: 1470404 (not found)

---

### update_section(guid, name=None)

Update section name.

**Params**: `guid` (string, required), `name` (string, optional)
**Returns**: `Dict` — updated section
**Errors**: 1470403 (no permission), 1470404 (not found)

---

### delete_section(guid)

Delete a section. Tasks in the section are moved to default section.

**Params**: `guid` (string, required)
**Returns**: `bool`
**Errors**: 1470403 (no permission), 1470404 (not found)

---

### list_section_tasks(guid, completed=None, created_from=None, created_to=None)

List tasks in a specific section.

**Params**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| guid | string | **Yes** | Section GUID |
| completed | bool | No | Filter by completion |
| created_from | string | No | Filter tasks created after this ms timestamp |
| created_to | string | No | Filter tasks created before this ms timestamp |

**Returns**: `List[Dict]` — task objects
**Errors**: 1470403 (no permission), 1470404 (section not found)

---

## Custom Fields

### list_custom_fields(resource_type=None, resource_id=None)

List custom fields for a resource.

**Params**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| resource_type | string | No | `"tasklist"` |
| resource_id | string | No | Tasklist GUID |

**Returns**: `List[Dict]` — custom field objects
**Errors**: 1470403 (no permission)

---

### create_custom_field(name, field_type, resource_type, resource_id, settings=None)

Create a custom field and attach it to a tasklist. Rate-limited to 100/min.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| name | string | **Yes** | Field name | max 50 chars |
| field_type | string | **Yes** | Field type | `number`\|`member`\|`datetime`\|`single_select`\|`multi_select`\|`text` |
| resource_type | string | **Yes** | `"tasklist"` | Only supported type |
| resource_id | string | **Yes** | Tasklist GUID to attach field to | — |
| settings | dict | No | Type-specific settings object | See api-validation.md for schemas |

**Returns**: `Dict` — created custom field with `guid`
**Errors**: 1470400 (missing settings for type), 1470403 (no edit permission), 1470404 (tasklist not found)

---

### get_custom_field(guid)

Get details of a custom field including its options.

**Params**: `guid` (string, required)
**Returns**: `Dict` — custom field with type-specific settings
**Errors**: 1470404 (not found)

---

### update_custom_field(guid, name=None, settings=None)

Update custom field name or settings.

**Params**: `guid` (required), `name` (optional), `settings` (optional, type-specific)
**Returns**: `Dict` — updated custom field
**Errors**: 1470403 (no permission), 1470404 (not found)

---

### add_custom_field_to_resource(guid, type, id)

Link an existing custom field to an additional tasklist.

**Params**: `guid` (field GUID), `type` (`"tasklist"`), `id` (tasklist GUID)
**Returns**: `bool`
**Errors**: 1470403 (no permission on field or resource), 1470404 (not found)

---

### remove_custom_field_from_resource(guid, type, id)

Unlink a custom field from a tasklist.

**Params**: `guid` (field GUID), `type` (`"tasklist"`), `id` (tasklist GUID)
**Returns**: `bool`
**Errors**: 1470403 (no permission), 1470404 (not found)

---

## Utilities

| Function | Output | Note |
|----------|--------|------|
| `datetime_to_task_timestamp(dt)` | str | Milliseconds string — for `due.timestamp`, `start.timestamp` |
| `is_task_completed(task)` | bool | Handles `"0"` string correctly |
| `get_today_range_ms()` | (int, int) | start_ms, end_ms for today |
| `format_timestamp_for_display(ts_ms)` | str | `"YYYY-MM-DD HH:MM"` |
