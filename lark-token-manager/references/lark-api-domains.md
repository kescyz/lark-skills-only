# Lark API Domains Catalog

Available domains for building Lark skills. All require `user_access_token` from `lark-token-manager`.

API docs located in: `docs/` folder of the kesflow-user-token-management project.

## Core Domains

### Calendar (`calendar-v4`)
**Scopes**: `calendar:calendar`, `calendar:calendar:readonly`
**Resources**: Calendar, Event, Attendee, FreeBusy, TimeOff, ExchangeBinding
**Key ops**: CRUD calendars/events, manage attendees, check free/busy, sync Exchange
**Docs path**: `docs/calendar-v4/`

### Task (`task-v2`)
**Scopes**: `task:task:read`, `task:task:write`, `task:tasklist:read`, `task:tasklist:write`, `task:section:read`, `task:section:write`, `task:custom_field:read`, `task:custom_field:write`, `task:comment:read`, `task:comment:write`
**Resources**: Task, Subtask, Tasklist, Section, Comment, CustomField, Attachment
**Key ops**: CRUD tasks/lists, manage members, dependencies, reminders, custom fields, comments
**Docs path**: `docs/task-v2/`

### Bitable / Base (`bitable-v1`)
**Scopes**: `bitable:app`
**Resources**: App, Table, View, Record, Field, Form, Dashboard, AdvancedPermission
**Key ops**: CRUD tables/records/fields, search records, manage views, advanced permissions
**Docs path**: `docs/docs/bitable-v1/`
**Note**: Also accessible via `Lark_Base_MCP_Server` tools with `user_access_token`

### Contact (`contact-v3`)
**Scopes**: `contact:contact`, `contact:contact.base:readonly`, `contact:contact:readonly_as_app`, `contact:user.base:readonly`, `contact:user.department:readonly`, `contact:user.email:readonly`, `contact:user.phone:readonly`, `contact:user.employee_id:readonly`, `contact:user.id:readonly`
**Resources**: User, Department, Group, FunctionalRole, CustomAttr, EmployeeTypeEnum
**Key ops**: Lookup users/departments, search org directory, manage groups, CRUD org members
**Docs path**: `docs/contact-v3/`

### IM - Instant Messaging (`im-v1`)
**Scopes**: `im:message`, `im:message:send_as_bot`, `im:message:send_multi_users`, `im:message:send_multi_depts`, `im:chat`, `im:chat:readonly`, `im:resource`
**Resources**: Message, Chat, Image, File, Pin, Reaction, BatchMessage, Card
**Key ops**: Send/receive messages, manage chats, upload images/files, message cards, batch broadcast
**Docs path**: `docs/im-v1/`

## Document Domains

### Drive (`drive-v1`)
**Scopes**: `drive:drive`, `drive:drive:readonly`
**Resources**: File, Folder, Upload, Download, Media, Permission, Comment, Search
**Key ops**: CRUD files/folders, upload/download, manage permissions, search, read doc comments
**Docs path**: `docs/docs/drive-v1/`

### Docs / Docx (`docx-v1`)
**Resources**: Document, DocumentBlock
**Key ops**: Create/read docs, manipulate block-level content (paragraphs, tables, images)
**Docs path**: `docs/docs/docs/`

### Sheets (`sheets-v3`)
**Resources**: Spreadsheet, Sheet, Data, RowCol, Filter, ConditionFormat, DataValidation
**Key ops**: CRUD spreadsheets, read/write cell data, merge/split, set styles, formulas
**Docs path**: `docs/docs/sheets-v3/`

### Wiki (`wiki-v2`)
**Resources**: Space, SpaceNode, SpaceMember, SpaceSetting
**Key ops**: CRUD wiki spaces/pages, manage members, move/copy nodes, search
**Docs path**: `docs/docs/wiki-v2/`

## Workflow Domains

### Approval (`approval-v4`)
**Scopes**: `approval:approval`, `approval:approval:readonly`
**Resources**: Approval, Instance, Task, Comment, ExternalApproval
**Key ops**: Create/manage approval flows, approve/reject tasks, search instances
**Docs path**: `docs/approval-v4/`
**Note**: Mostly uses `tenant_access_token`, check docs for user token support

### Attendance (`attendance-v1`)
**Resources**: Group, Shift, UserDailyShift, UserTask, UserStatsData, UserApproval
**Key ops**: Manage attendance groups/shifts, query check-in records, import data
**Docs path**: `docs/attendance-v1/`

## Suggested Skill Groupings

| Skill Name | Domains | Use Case |
|------------|---------|----------|
| `lark-calendar-manager` | calendar-v4 | Calendar & event management |
| `lark-task-manager` | task-v2 | Task & project tracking |
| `lark-base-manager` | bitable-v1 | No-code database / HR systems |
| `lark-docs-manager` | docx-v1, drive-v1, wiki-v2 | Document & knowledge management |
| `lark-messenger` | im-v1 | Chat & messaging automation |
| `lark-hr-manager` | contact-v3, attendance-v1, approval-v4 | HR & org directory |
| `lark-sheets-manager` | sheets-v3 | Spreadsheet automation |
