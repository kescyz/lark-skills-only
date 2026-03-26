# Lark Task API Validation Reference

> See [api-reference.md](./api-reference.md) for method signatures.
> See [api-examples.md](./api-examples.md) for code samples.

---

## Required Scopes

| Scope | Purpose |
|-------|---------|
| `task:task:read` | Read tasks, subtasks |
| `task:task:write` | Create, update, delete tasks/subtasks |
| `task:tasklist:read` | List and get tasklists |
| `task:tasklist:write` | Create, delete tasklists; manage members |
| `task:section:read` | List sections |
| `task:section:write` | Create, update, delete sections |
| `task:custom_field:read` | List, get custom fields |
| `task:custom_field:write` | Create, update custom fields; link/unlink to resources |
| `task:comment:read` | List task comments |
| `task:comment:write` | Add comments to tasks |

All scopes must be enabled in the Lark app console.

---

## member Format

Used in tasks (`members`) and tasklists (`members`).

```python
# Task member
{"id": "ou_xxx", "type": "user", "role": "assignee"}
{"id": "ou_xxx", "type": "user", "role": "follower"}

# Tasklist member
{"id": "ou_xxx", "type": "user", "role": "editor"}
{"id": "ou_xxx", "type": "user", "role": "viewer"}
{"id": "ou_xxx", "type": "user", "role": "owner"}  # read-only, auto-assigned to creator
```

**id**: Use `lark_open_id` from MCP `search_users` or MCP `whoami`.
**type**: Only `"user"` supported currently.
**Task roles**: `assignee` (read+edit), `follower` (read-only).
**Tasklist roles**: `owner` (full access), `editor` (edit tasks/sections), `viewer` (read-only).

**Constraints**: max 50 per task create request; max 500 per tasklist create.

---

## due / start Format

Both use the same schema. All timestamps in **milliseconds** (13-digit).

```python
# Specific date and time
{"timestamp": "1704355200000", "is_all_day": False}

# All-day date (only day precision matters; time portion ignored)
{"timestamp": "1704355200000", "is_all_day": True}

# Clear the due/start time
{"timestamp": "0"}
# OR just set the field to null in update_fields
```

**Constraints**:
- `timestamp` cannot be negative
- When both start and due are set: `start.timestamp <= due.timestamp`
- `start.is_all_day` and `due.is_all_day` must both be `true` or both `false`
- For moments, second-precision is retained (ms precision auto-truncated)
- For dates, day-precision is retained

---

## completed_at Quirk

`completed_at` is a string, not an int. Two special values:

```python
"0"                  # Task is NOT completed
"1704355200000"      # Task IS completed at this ms timestamp
```

**is_task_completed(task)** utility handles this:
```python
is_task_completed({"completed_at": "0"})            # False
is_task_completed({"completed_at": "1704355200000"}) # True
is_task_completed({"completed_at": ""})              # False
```

**Cannot** re-complete an already-completed task. Must uncomplete first (`"0"`), then complete again.

---

## repeat_rule Format

RRULE subset per RFC 5545. Requires `due` to be set.

```
FREQ=DAILY;INTERVAL=1                            # Daily
FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR     # Weekdays
FREQ=WEEKLY;INTERVAL=2;BYDAY=MO                  # Bi-weekly Monday
FREQ=MONTHLY;INTERVAL=1;WKST=MO;BYDAY=2FR        # 2nd Friday monthly
```

**Constraints**: max 1000 chars. Cannot update `repeat_rule` and `completed_at` simultaneously.

---

## Custom Field Type Settings

### number_setting
```python
{
    "format": "normal",    # normal | usd | cny | eur | custom
    "decimal_count": 2,    # decimal places
    "separator": "thousand" # none | thousand
}
```

### single_select_setting / multi_select_setting
```python
{
    "options": [
        {"name": "Option A", "color_index": 1},   # color_index: 0-26
        {"name": "Option B", "color_index": 11}
    ]
}
```
**color_index**: 0-26 integer (maps to preset colors in Lark UI).

### member_setting
```python
{"multi": True}   # allow multiple members; False = single member
```

### datetime_setting
```python
{"format": "yyyy/mm/dd"}   # display format in UI
```

### text_setting
```python
{}  # no additional settings required
```

---

## tasklist member Roles

| Role | Permissions |
|------|-------------|
| `owner` | Full control; auto-assigned to creator |
| `editor` | Can create/edit/delete tasks and sections |
| `viewer` | Read-only access |

Note: Same user cannot have multiple roles on one tasklist. If creator is set as editor, they still become owner.

---

## Rate Limits

| Operation | Limit |
|-----------|-------|
| create_task / create_subtask | 10/sec |
| update_task / delete_task | 10/sec |
| list_tasks / get_task | 1000/min, 50/sec |
| create_tasklist | 1000/min, 50/sec |
| create_section | 1000/min, 50/sec |
| create_custom_field | 100/min |
| add_custom_field_to_resource | 100/min |

---

## Error Code Reference

| Code | HTTP | Description | Fix |
|------|------|-------------|-----|
| 1470400 | 400 | Bad request params | Check required fields, types, constraints; read `msg` for specifics |
| 1470403 | 403 | Permission denied | Check calling identity has edit permission on resource |
| 1470404 | 404 | Resource not found | Verify GUID; resource may have been deleted |
| 1470422 | 500 | Concurrent calls with same client_token | Do not invoke concurrently with same token |
| 1470500 | 500 | Server error | Retry; contact support if persistent |

**Common 1470400 causes**:
- `summary` is empty or missing
- Setting `reminders` without setting `due`
- `repeat_rule` + `completed_at` updated simultaneously
- `repeat_rule` set when `due` is not set
- Re-completing an already-completed task
- `is_all_day` mismatch between `start` and `due`
- Both `insert_before` and `insert_after` set in create_section
