# Lark Base API Validation

> Field types, batch limits, filter syntax, rate limits, error codes.

## Field Type Codes

| Code | Type | Property Required | Notes |
|------|------|-------------------|-------|
| 1 | Text | No | UI variant: Barcode only ("Email" ui_type is API-invalid - only settable via Lark UI) |
| 2 | Number | No | UI variants: Currency, Progress, Rating |
| 3 | SingleSelect | Yes: `{options: [{name, color}]}` | Max 54 colors (0-53) |
| 4 | MultiSelect | Yes: `{options: [{name, color}]}` | Same as SingleSelect |
| 5 | Date | Optional: `{date_formatter, auto_fill}` | Value = Unix ms timestamp |
| 7 | Checkbox | No | Value: true/false |
| 11 | User | No | Value: `[{"id": "ou_xxx"}]` |
| 13 | Phone | No | |
| 15 | URL | No | Value: `{"text": "label", "link": "https://..."}` |
| 17 | Attachment | No | Requires lark-drive for upload |
| 18 | SingleLink | Yes: `{table_id, multiple}` | One-way link |
| 19 | Lookup | Yes: `{link_field_id, target_field_id}` | Read-only, auto-computed |
| 20 | Formula | Yes: `{formula_expression, formatter}` | Read-only, auto-computed |
| 21 | DuplexLink | Yes: `{table_id, multiple, back_field_name}` | Bidirectional link |
| 22 | Location | No | |
| 23 | GroupChat | No | |
| 1001 | CreatedTime | No | Auto, read-only |
| 1002 | ModifiedTime | No | Auto, read-only |
| 1003 | CreatedUser | No | Auto, read-only |
| 1004 | ModifiedUser | No | Auto, read-only |
| 1005 | AutoNumber | No | Auto, read-only |

## Batch Operation Limits

| Operation | Max Per Request | Semantics |
|-----------|----------------|-----------|
| batch_create_records | 500 | All-or-nothing |
| batch_update_records | 1000 | All-or-nothing |
| batch_delete_records | 1000 | All-or-nothing |
| batch_create_tables | No explicit limit | |
| batch_delete_tables | 1000 | |
| batch_add_role_members | 1000 | |
| batch_delete_role_members | 1000 | |

## Resource Limits

| Resource | Max |
|----------|-----|
| Tables per Base | 100 |
| Fields per table | 300 |
| Views per table | 200 |
| Records per list_records page | 500 |
| Roles per Base | 30 |
| Collaborators per Base | 200 |

## Filter Syntax

Formula-based filter for `list_records`:
```
CurrentValue.[Field Name]="value"
CurrentValue.[Number Field]>100
AND(CurrentValue.[Status]="Active", CurrentValue.[Date]>=1704067200000)
OR(CurrentValue.[Type]="A", CurrentValue.[Type]="B")
NOT(CurrentValue.[Archived]=true)
```

Date functions: dates are Unix millisecond timestamps.

## Sort Syntax

JSON string for `list_records`:
```json
[{"field_name": "Name", "desc": false}, {"field_name": "Date", "desc": true}]
```

## Rate Limits

| Category | Limit |
|----------|-------|
| Record create | 50 req/sec |
| Record list | 20 req/sec |
| Record write (update/delete) | 10 req/sec |
| Admin (app/table/field) | 20 req/min |
| Permission operations | 20 req/min |

## Required Scope

**Primary**: `bitable:app` — full CRUD for all Bitable resources.

**Optional** (for user info in responses):
- `contact:user.base:readonly` — user names, avatars
- `contact:user.employee_id:readonly` — user IDs

## Common Error Codes

| Code | Description | Fix |
|------|-------------|-----|
| 1254001 | Invalid app_token | Verify Base exists and token has access |
| 1254002 | Invalid table_id | Check table exists in this Base |
| 1254003 | Invalid record_id | Check record exists in this table |
| 1254006 | Field not found | Verify field_id |
| 1254007 | Field name conflict | Use unique field name |
| 1254040 | Max fields reached (300) | Delete unused fields |
| 1254043 | Cannot modify primary field type | Only rename allowed |
| 1254044 | Cannot delete primary field | |
| 1254045 | Cannot delete last view | Create another view first |
| 1254290 | Rate limit exceeded | Auto-retry in client (2s backoff) |
| 1254291 | Single-write lock conflict | Serialize writes to same table |
| 1254301 | Advanced permissions not enabled | `update_app(is_advanced=True)` first |
| 1254302 | Max roles reached (30) | Delete unused roles |
| 99992402 | Field validation failed (invalid ui_type) | Check valid ui_type values in Field Type Codes |
| 99991663 | Token expired | Re-fetch via MCP |
| 99991665 | Invalid token | Check token type |

## Known Limitations

- Cannot delete a Base app via API (manual cleanup only)
- New Base auto-creates 1 default table + 5 records
- Batch create is all-or-nothing — validate data before insertion
- Single concurrent write per table (serialize writes)
- Field update is full replace, not partial merge
- Attachment field requires lark-drive skill for file upload
- Formula and Lookup fields are read-only (auto-computed)
- `list_records` max 500 per page; use pagination for large tables
- `create_table` initial fields do NOT support `ui_type` or Number `formatter` (e.g., `"0%"`) - create field first, then `update_field` to add these properties
