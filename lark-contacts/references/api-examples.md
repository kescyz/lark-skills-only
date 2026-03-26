# Lark Contacts API Examples

> All examples assume client is initialized per SKILL.md.

## 1. Find someone and get full profile (MCP → get_user)

```python
# Step 1: Quick lookup via MCP (no Python needed)
# MCP search_users(query="Minh") → [{name, email, lark_open_id, department, ...}]
# Use lark_open_id from result

# Step 2: Full profile via API
user = client.get_user("ou_abc123")
print(f"Name: {user['name']}")
print(f"Job: {user.get('job_title', 'N/A')}")
print(f"Email: {user.get('email', 'N/A')}")
print(f"Status: {'Active' if user.get('status', {}).get('is_activated') else 'Inactive'}")
print(f"Joined: {user.get('join_time', 'N/A')}")
print(f"Depts: {user.get('department_ids', [])}")
```

## 2. Get full profile from email (single call)

```python
user = client.get_user_by_email("lan.nguyen@company.com")
if user:
    from utils import format_user_summary
    print(format_user_summary(user))
else:
    print("User not found")
```

## 3. List all people in a department

```python
# First: find department ID via search or org chart
members = client.list_department_members("od-marketing-dept-id")
print(f"Marketing has {len(members)} members:")
for user in members:
    print(f"  - {user['name']} ({user.get('job_title', '')})")

# Or use format helper
from utils import format_org_chart
chart = format_org_chart({"Marketing": members})
print(chart)
```

## 4. Browse org chart (root → children → members)

```python
# Get all top-level departments
top_depts = client.get_org_chart(dept_id="0")
print(f"Top-level departments: {len(top_depts)}")
for dept in top_depts:
    print(f"  {dept['name']} (id: {dept['open_department_id']})")

# Get full recursive tree from root
all_depts = client.get_org_chart(dept_id="0", fetch_child=True)
from utils import format_department_tree
print(format_department_tree(all_depts))

# Drill into a specific department
eng_children = client.get_org_chart(dept_id="od-engineering")
```

## 5. Resolve batch emails → Lark IDs (for messenger/calendar integration)

```python
emails = ["alice@company.com", "bob@company.com", "carol@company.com"]
result = client.batch_resolve_ids(emails=emails)

open_ids = []
not_found = []
for u in result.get("user_list", []):
    if u.get("user_id"):
        open_ids.append(u["user_id"])
    else:
        not_found.append(u.get("email", "unknown"))

print(f"Resolved: {len(open_ids)}, Not found: {not_found}")
# open_ids → pass to lark-messenger or lark-calendar
```

## 6. Get department ancestry path

```python
# Find where a department sits in the org hierarchy
path = client.get_department_path("od-frontend-team")
print("Department path (child → root):")
for dept in path:
    print(f"  {dept.get('name', dept.get('open_department_id'))}")
```

## 7. List groups and their members

```python
# List all company user groups
groups = client.list_groups()
print(f"Company has {len(groups)} user groups:")
for g in groups:
    print(f"  [{g['id']}] {g['name']}")

# Get detail + members for a specific group
group = client.get_group("project-managers-group-id")
print(f"\n{group['name']}: {group.get('description', '')}")

members = client.list_group_members("project-managers-group-id")
print(f"Members ({len(members)}):")
for m in members:
    print(f"  - open_id: {m['member_id']}")
```

## 8. Cross-skill: dept members → send group message (messenger integration)

```python
# Get all open_ids in Engineering department
members = client.list_department_members("od-engineering")
open_ids = [u["open_id"] for u in members if u.get("open_id")]

# Now pass to lark-messenger skill to create a group chat
# (handled by lark-messenger agent using tenant token)
# messenger_client.create_chat(name="Engineering Announcement", user_id_list=open_ids)
print(f"Ready to message {len(open_ids)} Engineering members")
```

## 9. Cross-skill: dept members → calendar invite

```python
# Get user_ids (not open_ids) for calendar invitations
members = client.list_department_members("od-design")
# Calendar uses user_id type for attendees
user_ids = [u.get("user_id") for u in members if u.get("user_id")]

# Or fetch with union_id type for other skills
# members = client.list_department_members("od-design")
# For calendar, typically pass open_ids as attendee user_ids
open_ids = [u["open_id"] for u in members]
print(f"Invite {len(open_ids)} Design team members to meeting")
```
