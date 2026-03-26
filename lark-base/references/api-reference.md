# Lark Base API Reference

> Token via `lark-token-manager` MCP. See [api-examples.md](./api-examples.md) for code samples. See [api-validation.md](./api-validation.md) for field types, constraints, error codes.

## LarkBaseClient

```python
from lark_api import LarkBaseClient
client = LarkBaseClient(
    access_token="t-xxx",       # user_access_token or tenant_access_token
    user_open_id="ou_xxx",
)
```

---

## App

### get_app(app_token)

Get Base metadata.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| app_token | str | Yes | Base identifier |

**Returns**: `Dict` — `{app_token, name, revision, is_advanced, time_zone}`

---

### create_app(name=None, folder_token=None)

Create new Base. Auto-creates 1 default table + 5 empty records.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| name | str | No | Base name (default: "未命名多维表格") |
| folder_token | str | No | Target folder (default: root) |

**Returns**: `Dict` — `{app, url}` where app has `app_token`, `name`, `default_table_id`

---

### update_app(app_token, name=None, is_advanced=None)

Update Base metadata. Set `is_advanced=True` to enable custom permission roles.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| app_token | str | Yes | Base identifier |
| name | str | No | New name |
| is_advanced | bool | No | Enable advanced permissions |

**Returns**: `Dict` — `{app}` with updated fields

---

### copy_app(app_token, name=None, folder_token=None, without_content=False)

Copy Base. `without_content=True` copies structure only (no records).

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| app_token | str | Yes | Source Base |
| name | str | No | New Base name |
| folder_token | str | No | Target folder |
| without_content | bool | No | Structure only (default: False) |

**Returns**: `Dict` — `{app}` with new `app_token`

---

## Table

### list_tables(app_token, page_size=100)

| Param | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| app_token | str | Yes | Base identifier | |
| page_size | int | No | Items per page | Max 100 (default: 100) |

**Returns**: `List[Dict]` — tables with `table_id`, `name`, `revision`

---

### create_table(app_token, name, fields=None)

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| app_token | str | Yes | Base identifier |
| name | str | Yes | Table name |
| fields | List[Dict] | No | Initial fields: `[{field_name, type, ui_type?, property?}]` |

**Returns**: `Dict` — `{table_id, default_view_id, field_id_list}`

---

### batch_create_tables(app_token, tables)

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| app_token | str | Yes | Base identifier |
| tables | List[Dict] | Yes | `[{name, fields?}]` |

**Returns**: `Dict` — `{table_ids: [...]}`

---

### update_table(app_token, table_id, name)

Rename table.

| Param | Type | Required |
|-------|------|----------|
| app_token | str | Yes |
| table_id | str | Yes |
| name | str | Yes |

---

### delete_table(app_token, table_id) / batch_delete_tables(app_token, table_ids)

Delete single table or up to 1000 tables. Cannot delete last table in Base.

---

## Field

### list_fields(app_token, table_id, page_size=100)

List all fields in table. Max 300 fields per table.

**Returns**: `List[Dict]` — fields with `field_id`, `field_name`, `type`, `ui_type`, `property`

---

### create_field(app_token, table_id, field_name, field_type, ui_type=None, description=None, property=None)

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| field_name | str | Yes | Display name |
| field_type | int | Yes | Type code (see api-validation.md) |
| ui_type | str | No | UI variant: Barcode, Currency, Progress, Rating (Note: "Email" is API-invalid, use plain Text type) |
| description | str | No | Field description |
| property | Dict | No | Type-specific config (see api-validation.md) |

**Returns**: `Dict` — `{field}` with `field_id`

**Errors**: 1254007 (field name conflict), 1254040 (max fields reached)

---

### update_field(app_token, table_id, field_id, field_name, field_type, ...)

**Full replace** — must include ALL desired properties. Omitted properties reset to defaults.

Same params as `create_field` plus `field_id`. **Errors**: 1254006 (field not found), 1254043 (cannot modify primary field type)

---

### delete_field(app_token, table_id, field_id)

Cannot delete primary field. **Errors**: 1254006 (not found), 1254044 (cannot delete primary)

---

## View

### list_views(app_token, table_id, page_size=100)

Max 200 views per table.

**Returns**: `List[Dict]` — views with `view_id`, `view_name`, `view_type`

---

### get_view(app_token, table_id, view_id)

**Returns**: `Dict` — `{view}` with `view_id`, `view_name`, `view_type`, `property`

---

### create_view(app_token, table_id, view_name, view_type)

| Param | Type | Required | Values |
|-------|------|----------|--------|
| view_name | str | Yes | Display name |
| view_type | str | Yes | `grid`, `kanban`, `gallery`, `gantt`, `form` |

**Returns**: `Dict` — `{view}` with `view_id`

---

### update_view(app_token, table_id, view_id, view_name) / delete_view(...)

Rename or delete view. Cannot delete last view in table.

---

## Record

### list_records(app_token, table_id, view_id=None, filter=None, sort=None, field_names=None, page_size=100, automatic_fields=False)

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| view_id | str | No | Filter by view |
| filter | str | No | Formula syntax: `CurrentValue.[Status]="Active"` |
| sort | str | No | JSON: `[{"field_name":"Name","desc":false}]` |
| field_names | str | No | JSON array of field names to return |
| page_size | int | No | Max 500 (default: 100) |
| automatic_fields | bool | No | Include auto fields (created_time, etc.) |

**Returns**: `List[Dict]` — records with `record_id`, `fields`

---

### get_record(app_token, table_id, record_id)

**Returns**: `Dict` — `{record}` with `record_id`, `fields`

---

### create_record(app_token, table_id, fields)

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| fields | Dict | Yes | `{field_name: value}` |

**Returns**: `Dict` — `{record}` with `record_id`

---

### batch_create_records(app_token, table_id, records, client_token=None)

Create up to 500 records. **All-or-nothing**: one bad record fails entire batch.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| records | List[Dict] | Yes | `[{"fields": {...}}]` |
| client_token | str | No | UUID for idempotent retry |

**Returns**: `Dict` — `{records: [{record_id}]}`

---

### update_record / batch_update_records

Single: `update_record(app_token, table_id, record_id, fields)` — partial update.
Batch: `batch_update_records(app_token, table_id, records)` — up to 1000, `records: [{record_id, fields}]`.

---

### delete_record / batch_delete_records

Single: `delete_record(app_token, table_id, record_id)`
Batch: `batch_delete_records(app_token, table_id, record_ids)` — up to 1000.

---

## Permission

### list_roles(app_token, page_size=100)

List custom roles. Max 30 roles per Base. Requires `is_advanced=True`.

**Returns**: `List[Dict]` — roles with `role_id`, `role_name`, `table_roles`, `block_roles`

---

### create_role(app_token, role_name, table_roles=None, block_roles=None)

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| role_name | str | Yes | Display name |
| table_roles | List[Dict] | No | `[{table_name, table_perm, rec_rule?, field_perm?}]` |
| block_roles | List[Dict] | No | `[{block_id, block_type, block_perm}]` |

**table_perm values**: 0=none, 1=read, 2=edit, 4=add-only

**Returns**: `Dict` — `{role}` with `role_id`

---

### update_role(app_token, role_id, role_name, table_roles=None, block_roles=None)

Full replace. Same params as `create_role` plus `role_id`.

---

### delete_role(app_token, role_id)

---

### list_role_members(app_token, role_id, page_size=100)

**Returns**: `List[Dict]` — `[{member_id, member_type, member_name}]`

---

### add_role_member(app_token, role_id, member_id, member_type="open_id")

| Param | Type | Required | Values |
|-------|------|----------|--------|
| member_id | str | Yes | User identifier |
| member_type | str | No | `open_id`, `union_id`, `user_id` |

---

### delete_role_member(app_token, role_id, member_id)

---

### batch_add_role_members(app_token, role_id, member_list)

Max 1000. `member_list: [{"member_id": "ou_xxx", "member_type": "open_id"}]`

---

### batch_delete_role_members(app_token, role_id, member_ids)

Max 1000. `member_ids: ["ou_xxx", ...]`
