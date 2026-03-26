# Lark Base API Examples

> All examples assume client initialized per SKILL.md.

## 1. Create Base with tables and fields (System Setup)

```python
from utils import (FIELD_TEXT, FIELD_NUMBER, FIELD_SINGLE_SELECT, FIELD_DATE,
                   FIELD_DUPLEX_LINK, build_select_options, build_link_property,
                   build_date_property)

# Create Base
result = client.create_app(name="Quản lý nhân sự")
app_token = result["app"]["app_token"]
default_table_id = result["app"]["default_table_id"]

# Create real tables with initial fields
dept_result = client.create_table(app_token, "G1. Danh sách phòng ban", fields=[
    {"field_name": "Tên phòng ban", "type": FIELD_TEXT},
    {"field_name": "Trưởng phòng", "type": FIELD_TEXT},
    {"field_name": "Số lượng", "type": FIELD_NUMBER},
])
dept_table_id = dept_result["table_id"]

staff_result = client.create_table(app_token, "1.1. Danh sách nhân viên", fields=[
    {"field_name": "Họ và tên", "type": FIELD_TEXT},
    {"field_name": "Email", "type": FIELD_TEXT},  # Note: ui_type "Email" is API-invalid, use plain Text
    {"field_name": "Trạng thái", "type": FIELD_SINGLE_SELECT,
     "property": build_select_options(["Đang làm", "Nghỉ phép", "Đã nghỉ"])},
    {"field_name": "Ngày vào", "type": FIELD_DATE,
     "property": build_date_property("yyyy-MM-dd")},
])
staff_table_id = staff_result["table_id"]

# Delete default table (now safe)
client.delete_table(app_token, default_table_id)
```

## 2. Create DuplexLink between tables (ERD)

```python
# Bidirectional link: Staff ↔ Department
client.create_field(
    app_token, staff_table_id,
    field_name="Phòng ban",
    field_type=FIELD_DUPLEX_LINK,
    property=build_link_property(
        table_id=dept_table_id,
        multiple=False,
        back_field_name="Nhân viên"  # auto-creates reverse field in dept table
    )
)
```

## 3. Batch insert records

```python
from utils import chunk_records

records = [
    {"fields": {"Họ và tên": "Nguyễn Văn A", "Email": "a@company.com",
                "Trạng thái": "Đang làm", "Ngày vào": 1704067200000}},
    {"fields": {"Họ và tên": "Trần Thị B", "Email": "b@company.com",
                "Trạng thái": "Đang làm", "Ngày vào": 1706745600000}},
    {"fields": {"Họ và tên": "Lê Văn C", "Email": "c@company.com",
                "Trạng thái": "Nghỉ phép", "Ngày vào": 1709424000000}},
]

# For large datasets, chunk into 500-record batches
for chunk in chunk_records(records, chunk_size=500):
    client.batch_create_records(app_token, staff_table_id, chunk)
```

## 4. Search and filter records

```python
# Filter by field value
active = client.list_records(
    app_token, staff_table_id,
    filter='CurrentValue.[Trạng thái]="Đang làm"'
)
print(f"Active staff: {len(active)}")

# Sort by date descending
recent = client.list_records(
    app_token, staff_table_id,
    sort='[{"field_name":"Ngày vào","desc":true}]',
    page_size=10
)

# Combined filter + sort
result = client.list_records(
    app_token, staff_table_id,
    filter='AND(CurrentValue.[Trạng thái]="Đang làm",CurrentValue.[Ngày vào]>=1704067200000)',
    sort='[{"field_name":"Họ và tên","desc":false}]'
)
```

## 5. Batch update records

```python
# Update multiple records
updates = [
    {"record_id": "rec_id_1", "fields": {"Trạng thái": "Đã nghỉ"}},
    {"record_id": "rec_id_2", "fields": {"Trạng thái": "Đã nghỉ"}},
]
client.batch_update_records(app_token, staff_table_id, updates)
```

## 6. View management

```python
# Create kanban view grouped by status
result = client.create_view(app_token, staff_table_id, "Theo trạng thái", "kanban")
view_id = result["view"]["view_id"]

# List all views
views = client.list_views(app_token, staff_table_id)
for v in views:
    print(f"  {v['view_name']} ({v['view_type']})")
```

## 7. Advanced permissions setup

```python
# Enable advanced permissions
client.update_app(app_token, is_advanced=True)

# Create read-only viewer role
client.create_role(app_token, "Viewer", table_roles=[
    {"table_name": "1.1. Danh sách nhân viên", "table_perm": 1},  # 1=read
    {"table_name": "G1. Danh sách phòng ban", "table_perm": 1},
])

# Create editor role for staff table only
role = client.create_role(app_token, "HR Editor", table_roles=[
    {"table_name": "1.1. Danh sách nhân viên", "table_perm": 2},  # 2=edit
    {"table_name": "G1. Danh sách phòng ban", "table_perm": 1},   # read-only
])
role_id = role["role"]["role_id"]

# Add member to role
client.add_role_member(app_token, role_id, "ou_user_open_id")

# Batch add members
client.batch_add_role_members(app_token, role_id, [
    {"member_id": "ou_user1", "member_type": "open_id"},
    {"member_id": "ou_user2", "member_type": "open_id"},
])
```

## 8. Cross-skill: contacts → Base user fields

```python
# Use lark-contacts to find user open_ids, then insert into User field
# User field (type 11) accepts: [{"id": "ou_xxx"}]
client.create_record(app_token, staff_table_id, {
    "Họ và tên": "Phạm Văn D",
    "Người quản lý": [{"id": "ou_manager_open_id"}],  # User field
})
```
