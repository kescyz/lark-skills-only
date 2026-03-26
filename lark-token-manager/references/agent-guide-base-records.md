# Agent Guide: CSV/JSON -> Lark Base Records

How to parse structured data into Bitable record format before batch API calls.

## Core Concepts

- Batch create: max **500 records/request** (all-or-nothing semantics)
- **26+ field types** with specific value formats
- **One write at a time** per Base (no concurrent writes)
- Default table quirk: new Base creates 1 table + 5 dummy records

## Data Type Mapping

### CSV/JSON Type -> Lark Field Type

| Source Type | Lark Field Type | `type` Value | Value Format |
|-------------|----------------|-------------|--------------|
| string | Text | 1 | `"hello"` |
| number | Number | 2 | `123.45` |
| enum (single) | SingleSelect | 3 | `"Option A"` |
| enum (multi) | MultiSelect | 4 | `["A", "B"]` |
| date/datetime | DateTime | 5 | `1704067200000` (ms timestamp) |
| boolean | Checkbox | 7 | `true` / `false` |
| url | URL | 15 | `{ "text": "title", "link": "https://..." }` |
| email | Text (email UI) | 1 | `"user@example.com"` |
| phone | Phone | 13 | `"+84123456789"` |
| currency | Number (currency UI) | 2 | `99.99` |
| person/user | User | 11 | `[{"id": "ou_xxx"}]` |
| reference/FK | Link | 18 | `["recXXX", "recYYY"]` (record IDs) |

### Field Creation Format

```json
{
  "field_name": "Priority",
  "type": 3,
  "property": {
    "options": [
      {"name": "P0", "color": 0},
      {"name": "P1", "color": 1},
      {"name": "P2", "color": 2}
    ]
  }
}
```

## Import Strategy

### Step 1: Parse Input Data

```python
import csv, json

# CSV
with open("data.csv") as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    rows = list(reader)

# JSON
data = json.loads(json_string)
headers = list(data[0].keys())
rows = data
```

### Step 2: Infer Field Types

```python
def infer_field_type(values):
    """Infer Lark field type from sample values."""
    sample = [v for v in values[:20] if v]
    if not sample:
        return 1  # Text fallback

    # Check numeric
    try:
        [float(v) for v in sample]
        return 2  # Number
    except ValueError:
        pass

    # Check date patterns
    import re
    date_pattern = r'\d{4}[-/]\d{2}[-/]\d{2}'
    if all(re.match(date_pattern, str(v)) for v in sample):
        return 5  # DateTime

    # Check boolean
    if all(str(v).lower() in ('true','false','yes','no','0','1') for v in sample):
        return 7  # Checkbox

    # Check low-cardinality -> SingleSelect
    unique = set(str(v) for v in sample)
    if len(unique) <= 10 and len(sample) >= 5:
        return 3  # SingleSelect

    return 1  # Text
```

### Step 3: Create Base & Tables

```python
# 1. Create Base
base = client.create_base({"name": "Imported Data"})
app_token = base["app"]["app_token"]

# 2. Get default table (auto-created)
tables = client.list_tables(app_token)
default_table_id = tables[0]["table_id"]

# 3. Create your tables with fields
new_table = client.create_table(app_token, {
    "table": {
        "name": "Employees",
        "default_view_name": "Grid View",
        "fields": [
            {"field_name": "Name", "type": 1},
            {"field_name": "Department", "type": 3, "property": {
                "options": [{"name": "Engineering"}, {"name": "Sales"}]
            }},
            {"field_name": "Salary", "type": 2},
            {"field_name": "Start Date", "type": 5}
        ]
    }
})
table_id = new_table["table_id"]

# 4. Delete default table (after creating yours)
client.delete_table(app_token, default_table_id)
```

### Step 4: Batch Insert Records

```python
def batch_insert(client, app_token, table_id, records):
    """Insert records in chunks of 500."""
    results = []
    for i in range(0, len(records), 500):
        chunk = records[i:i+500]
        batch_data = {
            "records": [{"fields": r} for r in chunk]
        }
        result = client.create_records(app_token, table_id, batch_data)
        results.extend(result.get("records", []))
        if i + 500 < len(records):
            time.sleep(0.02)  # Respect 50 req/s
    return results
```

### Step 5: Validate Before Insert

All-or-nothing means one bad record kills the entire batch. Validate first:

```python
def validate_record(record, field_schema):
    """Pre-validate record against field types."""
    errors = []
    for field_name, value in record.items():
        field = field_schema.get(field_name)
        if not field:
            errors.append(f"Unknown field: {field_name}")
            continue
        if field["type"] == 2 and value:  # Number
            try:
                float(value)
            except (ValueError, TypeError):
                errors.append(f"{field_name}: '{value}' not a number")
        if field["type"] == 5 and value:  # DateTime
            if not isinstance(value, (int, float)):
                errors.append(f"{field_name}: expected ms timestamp")
    return errors
```

## Default Table Handling

When creating a new Base:
1. Lark auto-creates 1 default table with 5 dummy records
2. You **cannot** delete the default table if it's the only table
3. Strategy: Create ALL your tables first, THEN delete the default table

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Create records (batch) | 50 req/s, 500 records/req |
| List records | 20 req/s, 500 records/page |
| Update records (batch) | 50 req/s, 1000 records/req |
| Delete records (batch) | 50 req/s, 1000 records/req |
| Create table | 50 req/s |

## Required Scopes

- `bitable:app` — Full Base read/write
- `bitable:app:readonly` — Read-only access

---

## Custom Skill Builder Concept

> **Status:** Concept only. Actual implementation is future work.

A **meta-skill** that generates specialized Base skills from ERD or business requirements.

### Input
User provides system requirements:
> "HR management system with employees, departments, leave tracking, performance reviews"

### Process
1. **Analyze requirements** -> extract entities, relationships, workflows
2. **Generate table schemas** (field types, links, formulas)
3. **Create `lark_api.py`** with domain-specific methods: `create_employee()`, `approve_leave()`, `calculate_performance_score()`
4. **Generate SKILL.md** with domain-specific triggers and examples
5. **Package as plugin** with `plugin.json`

### Example Output

For "HR Management System":

**Tables generated:**
- `employees` (Name, Department[link], Position, Salary, Start Date, Status)
- `departments` (Name, Manager[link->employees], Budget, Headcount[formula])
- `leave_requests` (Employee[link], Type[select], Start, End, Status[select], Approved By[link])
- `performance_reviews` (Employee[link], Period, Score, Reviewer[link], Notes)

**Methods generated:**
```python
class LarkHRClient(LarkAPIBase):
    def create_employee(self, name, department, position, salary): ...
    def submit_leave_request(self, employee_id, leave_type, start, end): ...
    def approve_leave(self, request_id, approver_id): ...
    def get_department_headcount(self, department_id): ...
    def create_performance_review(self, employee_id, period, score): ...
```

This is SEPARATE from `lark-base` (generic Base CRUD). Custom skill builder generates **specialized skills** using Base API for specific business domains.
