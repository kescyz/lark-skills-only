# Lark Sheets API Examples

> All examples assume client initialized per [SKILL.md](../SKILL.md).
> See [api-reference.md](./api-reference.md) for param details.
> See [api-validation.md](./api-validation.md) for enums and error codes.

---

## 1. Create Spreadsheet and Populate with Data

```python
# Create spreadsheet
result = client.create_spreadsheet("Báo cáo doanh thu Q1 2026")
token = result["spreadsheet"]["spreadsheet_token"]

# Get first sheet
sheets = client.query_sheets(token)
sheet_id = sheets[0]["sheet_id"]

# Write headers
headers = [["STT", "Nhân viên", "Khu vực", "Doanh thu", "Ghi chú"]]
client.write_range(token, make_range(sheet_id, "A1", "E1"), headers)

# Append data rows
rows = [
    [1, "Nguyễn Văn A", "Hà Nội",  85_000_000, "Đạt chỉ tiêu"],
    [2, "Trần Thị B",   "TP.HCM",  120_000_000, "Vượt chỉ tiêu"],
    [3, "Lê Văn C",     "Đà Nẵng", 60_000_000, "Cần cải thiện"],
]
client.append_data(token, make_range(sheet_id, "A1", "E1"), rows, insert_data_option="INSERT_ROWS")

print(f"Spreadsheet: {result['spreadsheet']['url']}")
```

---

## 2. Read Data from Range and Process

```python
token = "existing_spreadsheet_token"
sheets = client.query_sheets(token)
sheet_id = sheets[0]["sheet_id"]

# Read with unformatted values for numeric processing
data = client.read_range(
    token,
    make_range(sheet_id, "A1", "E100"),
    value_render="UnformattedValue"
)
rows = data["valueRange"].get("values") or []

# Skip header row, sum revenue column (index 3)
total = sum(row[3] for row in rows[1:] if len(row) > 3 and row[3])
print(f"Tổng doanh thu: {total:,} VND")

# Read multiple ranges at once
results = client.batch_read_ranges(
    token,
    [make_range(sheet_id, "A1", "E1"), make_range(sheet_id, "D2", "D100")],
    value_render="UnformattedValue"
)
headers_row = results["valueRanges"][0]["values"][0]
revenue_col  = [r[0] for r in results["valueRanges"][1].get("values") or [] if r]
```

---

## 3. Add New Sheet, Write Headers, Append Rows

```python
token = "existing_spreadsheet_token"

# Add new sheet at index 1
client.operate_sheets(token, [
    {"addSheet": {"properties": {"title": "Tháng 4", "index": 1}}}
])

# Get the new sheet's ID
sheets = client.query_sheets(token)
new_sheet = next(s for s in sheets if s["title"] == "Tháng 4")
sheet_id = new_sheet["sheet_id"]

# Write headers
client.write_range(
    token,
    make_range(sheet_id, "A1", "D1"),
    [["Ngày", "Sản phẩm", "Số lượng", "Thành tiền"]]
)

# Append multiple data rows
import datetime
today = datetime.date.today().isoformat()
client.append_data(token, make_range(sheet_id, "A1", "D1"), [
    [today, "Laptop Dell",  2, 30_000_000],
    [today, "Màn hình LG",  5, 12_500_000],
    [today, "Chuột Logitech", 10, 1_500_000],
])
```

---

## 4. Find and Replace Values

```python
token = "existing_spreadsheet_token"
sheets = client.query_sheets(token)
sheet_id = sheets[0]["sheet_id"]

# Find cells containing "Cần cải thiện"
result = client.find_cells(
    token, sheet_id,
    find="Cần cải thiện",
    condition={"match_entire_cell": True, "match_case": False}
)
matched = result.get("find_result", {}).get("matched_cells") or []
print(f"Found {len(matched)} cells: {matched}")

# Overwrite found cell positions with new value
for cell in matched:
    row, col = cell["row"], cell["col"]
    letter = col_to_letter(col)
    rng = make_range(sheet_id, f"{letter}{row}")
    client.write_range(token, rng, [["Đang cải thiện"]])
```

---

## 5. Merge Header Cells Across Columns

```python
token = "existing_spreadsheet_token"
sheets = client.query_sheets(token)
sheet_id = sheets[0]["sheet_id"]

# Write a title spanning A1:E1
client.write_range(token, make_range(sheet_id, "A1"), [["BÁO CÁO DOANH THU Q1 2026"]])

# Merge A1:E1 into one cell
client.merge_cells(token, make_range(sheet_id, "A1", "E1"), merge_type="MERGE_ALL")

# Merge each row in B2:C10 horizontally (merge within each row)
client.merge_cells(token, make_range(sheet_id, "B2", "C10"), merge_type="MERGE_ROWS")

# Undo a merge if needed
client.unmerge_cells(token, make_range(sheet_id, "A1", "E1"))
```

---

## 6. Insert and Delete Rows Dynamically

```python
token = "existing_spreadsheet_token"
sheets = client.query_sheets(token)
sheet_id = sheets[0]["sheet_id"]

# Insert 3 blank rows before row index 1 (after header at row 0)
# Inherits formatting from the row BEFORE (index 0 = header)
client.insert_dimension(
    token, sheet_id,
    major_dimension="ROWS",
    start_index=1,
    end_index=4,        # inserts rows 1,2,3 (end_index exclusive)
    inherit_style="BEFORE"
)

# Write into the newly inserted rows
client.write_range(token, make_range(sheet_id, "A2", "D4"), [
    ["2026-04-01", "Phòng Kỹ thuật", 3, "Ưu tiên cao"],
    ["2026-04-02", "Phòng Marketing", 1, "Ưu tiên trung bình"],
    ["2026-04-03", "Phòng Kinh doanh", 5, "Ưu tiên cao"],
])

# Delete rows 10-14 (0-based indices, end exclusive = rows 11-15 in UI)
client.delete_dimension(
    token, sheet_id,
    major_dimension="ROWS",
    start_index=10,
    end_index=15
)

# Delete column D (index 3, 0-based)
client.delete_dimension(
    token, sheet_id,
    major_dimension="COLUMNS",
    start_index=3,
    end_index=4
)
```
