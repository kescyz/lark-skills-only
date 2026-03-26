# Lark Contacts API Validation

> Scopes, rate limits, constraints, error codes.

## Required Scopes

### Minimum Read-Only
`contact:contact.base:readonly` — unlocks name, en_name, avatar, status

### Recommended Full Read
```
contact:contact                     # CRUD users/departments (admin write ops)
contact:contact:readonly_as_app     # general read access as app
contact:contact.base:readonly       # name, en_name, avatar, status (base fields)
contact:user.base:readonly          # name, en_name, nickname, avatar
contact:user.department:readonly    # department_ids, leader_user_id
contact:user.employee:readonly      # status, city, join_time, job_title, employee_type, custom_attrs
contact:user.email:readonly         # email, enterprise_email
contact:user.phone:readonly         # mobile
contact:user.employee_id:readonly   # user_id field
contact:group:readonly              # list/get groups and members
contact:user.id:readonly            # batch_get_id (batch_resolve_ids)
```

## Scope → User Field Mapping

| Scope | Fields Unlocked |
|-------|----------------|
| Always returned | `open_id`, `union_id`, `avatar_key`, `mobile_visible` |
| `contact:user.base:readonly` | `name`, `en_name`, `nickname`, `avatar` (72/240/640/origin URLs) |
| `contact:user.email:readonly` | `email`, `enterprise_email` |
| `contact:user.phone:readonly` | `mobile` |
| `contact:user.gender:readonly` | `gender` (0=Unknown, 1=Male, 2=Female, 3=Other) |
| `contact:user.employee:readonly` | `status`, `city`, `country`, `work_station`, `join_time`, `is_tenant_manager`, `employee_no`, `employee_type`, `custom_attrs`, `job_title` |
| `contact:user.department:readonly` | `department_ids`, `leader_user_id`, `orders` |
| `contact:user.employee_id:readonly` | `user_id` |
| `contact:user.job_level:readonly` | `job_level_id` |
| `contact:user.job_family:readonly` | `job_family_id` |
| `contact:user.department_path:readonly` | `department_path` (user_access_token ONLY) |
| `contact:user.dotted_line_leader_info.read` | `dotted_line_leader_user_ids` |
| `contact:user.assign_info:read` | `assign_info` (license/seat details) |
| `contact:user.geo` | `geo` |

## Scope → Department Field Mapping

| Scope | Fields Unlocked |
|-------|----------------|
| Always returned | `open_department_id` |
| `contact:department.base:readonly` | `name`, `i18n_name`, `department_id`, `chat_id`, `status.is_deleted` |
| `contact:department.organize:readonly` | `parent_department_id`, `leader_user_id`, `order`, `unit_ids`, `member_count`, `leaders`, `group_chat_employee_types` |

## Token Requirements

All methods use **tenant_access_token** from MCP `get_tenant_token()`.

| Method | Notes |
|--------|-------|
| `get_user` | `department_path` field not available with tenant token |
| `list_department_members` | |
| `get_user_by_email` | Calls batch_resolve_ids → get_user internally |
| `batch_resolve_ids` | |
| `get_department` | |
| `get_org_chart` | |
| `get_department_path` | |
| `list_groups` | |
| `get_group` | |
| `list_group_members` | |

## Rate Limits

| Resource | Limit |
|----------|-------|
| User GET / PATCH | 1000/min, 50/sec |
| Department operations | No explicit limit documented |
| Department search | No explicit limit documented |
| Group simplelist | No explicit limit documented |
| Functional Role APIs | 100/min (not used by this skill) |

## Hard Constraints

| Constraint | Value |
|-----------|-------|
| `batch_resolve_ids` max emails | 50 |
| `batch_resolve_ids` max mobiles | 50 |
| `find_by_department` page_size max | 50 |
| dept children page_size max | 50 |
| group `simplelist` page_size max | 100 |
| Users per department | 500 |
| Departments per user | 50 |
| User groups per company | 500 |
| Root department ID | `"0"` |
| dept_id format | `^0\|[^od][A-Za-z0-9]*` (max 64 chars) |
| user_id max length | 64 chars, no spaces |
| group name max length | 100 chars |
| group description max length | 500 chars |
| Group member add/remove | One at a time (no batch) |

## user_id_type Values

| Value | Description |
|-------|-------------|
| `open_id` | App-specific user ID (default, recommended) |
| `union_id` | Cross-app user ID within same ISV |
| `user_id` | Org-internal user ID (requires `contact:user.employee_id:readonly`) |

## employee_type Values

| Value | Description |
|-------|-------------|
| `1` | Regular employee |
| `2` | Intern |
| `3` | Outsourcing |
| `4` | Contractor |
| `5` | Consultant |

## batch_resolve_ids: status Values

| Value | Description |
|-------|-------------|
| `0` | Not found |
| `1` | Active user found |
| `2` | Resigned user (only when `include_resigned=True`) |

## Common Error Codes

| Code | Description | Fix |
|------|-------------|-----|
| 1220003 | User not found | Verify user_id and id_type |
| 1220004 | Department not found | Verify dept_id and id_type |
| 1220401 | Insufficient permission | Check app scopes in Lark admin |
| 99991663 | Token expired | Re-fetch token via MCP |
| 99991665 | Invalid token | Use correct token type (user vs tenant) |
| 1254290 | Rate limit exceeded | Automatic retry in client (2s backoff) |
| 230002 | Tenant token required | Use `get_tenant_token()` from MCP |

## Known Limitations

- No list-all-users endpoint — must iterate departments via `list_department_members`
- `batch_resolve_ids` resolves personal email only, not corporate/enterprise email
- `search_departments` not available (requires user_access_token) — use MCP search_users or browse via get_org_chart
- `get_department_path` returns ancestors within app's contact scope only
- Group member add/remove is one-at-a-time (no bulk operation)
- `department_path` field on user only available via user_access_token (not tenant)
- `get_org_chart(fetch_child=True)` limited by app's contact scope
