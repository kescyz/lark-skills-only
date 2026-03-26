# Lark Contacts API Reference

> Token management via `lark-token-manager` MCP.
> See [api-examples.md](./api-examples.md) for code samples.
> See [api-validation.md](./api-validation.md) for scopes, constraints, error codes.

## LarkContactsClient

```python
from lark_api import LarkContactsClient
client = LarkContactsClient(
    access_token="t-xxx",       # tenant_access_token from MCP get_tenant_token()
    user_open_id="ou_xxx",
)
```

---

## People

### get_user(user_id, id_type="open_id")

Get full user profile. Returns 30+ fields depending on app scopes.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| user_id | string | Yes | User identifier | open_id / union_id / user_id |
| id_type | string | No | ID type | `open_id` \| `union_id` \| `user_id` (default: `open_id`) |

**Returns**: `Dict` — user object with fields gated by scope (see api-validation.md)

**Key return fields** (scope dependent):
- Always: `open_id`, `union_id`, `avatar_key`
- Base scope: `name`, `en_name`, `nickname`, `avatar`
- Employee scope: `status`, `city`, `join_time`, `employee_no`, `employee_type`, `job_title`, `custom_attrs`
- Department scope: `department_ids`, `leader_user_id`
- Email scope: `email`, `enterprise_email`
- Note: `department_path` field not available with tenant_access_token

**Errors**: 1220003 (user not found), 1220401 (no permission)

---

### list_department_members(dept_id, page_size=50)

List all users in a department. Pagination handled internally.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| dept_id | string | Yes | Department open_id | Root dept = `"0"` |
| page_size | int | No | Items per page | Max 50 (default: 50) |

**Returns**: `List[Dict]` — list of full user objects

**Errors**: 1220004 (dept not found), 1220401 (no permission)

---

### get_user_by_email(email)

Convenience: resolve email → open_id → full profile. Single call for common pattern.

**Params**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Personal email (not corporate/enterprise email) |

**Returns**: `Dict` (full user object) or `None` if not found

**Note**: Internally calls `batch_resolve_ids` then `get_user`.

---

### batch_resolve_ids(emails=None, mobiles=None, include_resigned=False)

Resolve up to 50 emails + 50 mobiles → Lark user IDs.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| emails | List[str] | No | Personal emails to resolve | Max 50; use personal not corporate |
| mobiles | List[str] | No | Mobile numbers to resolve | Max 50; include country code (e.g. `+84901234567`) |
| include_resigned | bool | No | Include resigned users | Default: `False` |

**Returns**: `Dict` with `user_list: [{user_id, email?, mobile?, status}]`
- `user_id` = open_id (when `user_id_type=open_id`)
- `status`: 0=not found, 1=found, 2=resigned (when include_resigned=True)

**Errors**: 1220401 (no scope `contact:user.id:readonly`)

---

## Departments

### get_department(dept_id, id_type="department_id")

Get department info.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| dept_id | string | Yes | Department identifier | Root dept = `"0"` |
| id_type | string | No | ID type | `department_id` \| `open_department_id` (default: `department_id`) |

**Returns**: `Dict` — department object

**Key return fields** (scope dependent):
- Base scope: `name`, `i18n_name`, `department_id`, `open_department_id`, `chat_id`, `status.is_deleted`
- Organize scope: `parent_department_id`, `leader_user_id`, `order`, `member_count`, `leaders[]`

**Errors**: 1220004 (dept not found)

---

### get_org_chart(dept_id="0", fetch_child=False, page_size=50)

Get child departments of a parent. Optionally recursive.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| dept_id | string | No | Parent department open_id | Default `"0"` = company root |
| fetch_child | bool | No | Recursive subtree | `True`: all descendants (user token: up to 1000) |
| page_size | int | No | Items per page | Max 50 (default: 50) |

**Returns**: `List[Dict]` — flat list of department objects

**Note**: `fetch_child=True` limited to depts within app's contact scope.

---

### get_department_path(dept_id, id_type="department_id")

Get ancestor chain from department up to root.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| dept_id | string | Yes | Department identifier | |
| id_type | string | No | ID type | `department_id` \| `open_department_id` (default: `department_id`) |

**Returns**: `List[Dict]` — departments ordered from queried dept toward root, limited by app's contact scope

---

## Groups

### list_groups(page_size=100)

List all user groups in the company.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| page_size | int | No | Items per page | Max 100 (default: 100) |

**Returns**: `List[Dict]` — list of `{id, name}` group objects

---

### get_group(group_id)

Get user group detail.

**Params**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| group_id | string | Yes | Group ID |

**Returns**: `Dict` — group object: `group_id`, `name`, `description`, `type` (1=Common), `member_count`

---

### list_group_members(group_id, member_id_type="open_id")

List all members of a user group. Pagination handled internally.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| group_id | string | Yes | Group ID | |
| member_id_type | string | No | ID type for returned members | `open_id` \| `union_id` \| `user_id` (default: `open_id`) |

**Returns**: `List[Dict]` — list of `{member_id}` objects

**Note**: Groups currently support users only (departments may be added in future API version).
