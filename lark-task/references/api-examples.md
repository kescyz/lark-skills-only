# Lark Task API Examples

> All examples assume the client is initialized per [SKILL.md](../SKILL.md).
> See [api-reference.md](./api-reference.md) for param details.
> See [api-validation.md](./api-validation.md) for enums, error codes.

---

## 1. Create Task with Deadline and Assignee

```python
from datetime import datetime, timedelta
from utils import datetime_to_task_timestamp

# Deadline: this Friday at 5 PM
friday = datetime.now()
days_to_friday = (4 - friday.weekday()) % 7 or 7
friday = (friday + timedelta(days=days_to_friday)).replace(
    hour=17, minute=0, second=0, microsecond=0
)

# Get assignee open_id from MCP: search_users(query="Alice")
task = client.create_task({
    "summary": "Write Q1 report",
    "description": "Include revenue breakdown and team highlights.",
    "due": {
        "timestamp": datetime_to_task_timestamp(friday),
        "is_all_day": False
    },
    "members": [
        {"id": "ou_alice_open_id", "type": "user", "role": "assignee"},
        {"id": "ou_bob_open_id", "type": "user", "role": "follower"}
    ]
})
print(f"Task created: {task['guid']}")
```

---

## 2. Create Subtask from Parent

```python
parent_task = client.create_task({
    "summary": "Launch new feature",
    "due": {"timestamp": datetime_to_task_timestamp(friday), "is_all_day": False}
})

# Create subtasks under the parent
subtasks = [
    "Write unit tests",
    "Update documentation",
    "Deploy to staging"
]
for title in subtasks:
    sub = client.create_subtask(parent_task["guid"], {
        "summary": title,
        "due": {"timestamp": datetime_to_task_timestamp(friday), "is_all_day": False}
    })
    print(f"Subtask: {sub['guid']} — {title}")
```

---

## 3. Complete and Uncomplete a Task

```python
import time

# Complete task
completed_ms = str(int(time.time() * 1000))
client.update_task(task["guid"], {
    "task": {"completed_at": completed_ms},
    "update_fields": ["completed_at"]
})

# Verify
t = client.get_task(task["guid"])
print(f"Completed: {is_task_completed(t)}")  # True

# Uncomplete task
client.update_task(task["guid"], {
    "task": {"completed_at": "0"},
    "update_fields": ["completed_at"]
})
```

---

## 4. Set Up Kanban Sections in a Tasklist

```python
# Create tasklist
tasklist = client.create_tasklist("Sprint 1")
tl_guid = tasklist["guid"]

# Create kanban columns in order
for name in ["Backlog", "In Progress", "Review", "Done"]:
    section = client.create_section(
        name=name,
        resource_type="tasklist",
        resource_id=tl_guid
    )
    print(f"Section: {section['guid']} — {name}")

# Verify sections
sections = client.list_sections("tasklist", tl_guid)
print(f"{len(sections)} sections created")
```

---

## 5. Create Custom Field and Add to Tasklist

```python
# Create single_select priority field
field = client.create_custom_field(
    name="Priority",
    field_type="single_select",
    resource_type="tasklist",
    resource_id=tl_guid,
    settings={
        "single_select_setting": {
            "options": [
                {"name": "P1 - Critical", "color_index": 1},
                {"name": "P2 - High",     "color_index": 11},
                {"name": "P3 - Medium",   "color_index": 16},
                {"name": "P4 - Low",      "color_index": 0}
            ]
        }
    }
)
field_guid = field["guid"]
print(f"Custom field created: {field_guid}")

# Field is already attached to tl_guid (from create)
# To attach to another tasklist:
client.add_custom_field_to_resource(field_guid, "tasklist", other_tl_guid)
```

---

## 6. Full Workflow: Create Tasklist → Sections → Tasks

```python
from datetime import datetime, timedelta
from utils import datetime_to_task_timestamp

# Step 1: Create project tasklist
tasklist = client.create_tasklist("Website Redesign")
tl_guid = tasklist["guid"]

# Step 2: Create sections
sections = {}
for name in ["Design", "Development", "Testing"]:
    s = client.create_section(name=name, resource_type="tasklist", resource_id=tl_guid)
    sections[name] = s["guid"]

# Step 3: Create tasks and add to tasklist + section
sprint_end = (datetime.now() + timedelta(weeks=2)).replace(
    hour=18, minute=0, second=0, microsecond=0
)
due_ms = datetime_to_task_timestamp(sprint_end)

design_tasks = ["Create wireframes", "Design system components"]
for title in design_tasks:
    t = client.create_task({
        "summary": title,
        "due": {"timestamp": due_ms, "is_all_day": False},
        "tasklists": [{"tasklist_guid": tl_guid, "section_guid": sections["Design"]}]
    })
    print(f"Task '{title}' created in Design section: {t['guid']}")

# Step 4: Check progress
all_tasks = client.get_tasklist_tasks(tl_guid)
done = [t for t in all_tasks if is_task_completed(t)]
pct = len(done) * 100 // len(all_tasks) if all_tasks else 0
print(f"Progress: {len(done)}/{len(all_tasks)} ({pct}%)")
```

---

## 7. Create Number Custom Field

```python
cost_field = client.create_custom_field(
    name="Estimated Cost",
    field_type="number",
    resource_type="tasklist",
    resource_id=tl_guid,
    settings={
        "number_setting": {
            "format": "usd",       # normal | usd | cny | eur | custom
            "decimal_count": 2,
            "separator": "thousand"  # none | thousand
        }
    }
)
```

---

## 8. List Tasks by Section and Check Completion

```python
# Get sections for tasklist
sections = client.list_sections("tasklist", tl_guid)

for section in sections:
    tasks = client.list_section_tasks(section["guid"])
    done = sum(1 for t in tasks if is_task_completed(t))
    print(f"{section['name']}: {done}/{len(tasks)} done")
```
