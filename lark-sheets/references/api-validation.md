# Lark Sheets Validation Reference

> See [api-reference.md](./api-reference.md) for method signatures.
> See [api-examples.md](./api-examples.md) for code samples.

---

## A1 Notation Rules

| Pattern | Meaning | Example |
|---------|---------|---------|
| `sheetId!A1` | Single cell | `abc123!B5` |
| `sheetId!A1:C3` | Cell range | `abc123!A1:D10` |
| `sheetId!A:D` | Full columns A through D | `abc123!A:D` |
| `sheetId!1:10` | Full rows 1 through 10 | `abc123!1:5` |

- `sheetId` is the `sheet_id` from `query_sheets()` — **not** the sheet title
- Column letters: A–Z (1–26), AA–AZ (27–52), BA–BZ (53–78), etc.
- Row numbers are **1-based**
- Use `make_range(sheet_id, start, end)` to build safely
- Use `col_to_letter(n)` / `letter_to_col(s)` for column conversion

---

## Write Limits

| Constraint | Limit |
|-----------|-------|
| Max rows per write | 5,000 |
| Max columns per write | 100 |
| Max chars per cell | 50,000 |
| Max ranges per batch_write | no hard limit (keep under 20 for safety) |
| Max rows/cols per dimension delete | 5,000 |

---

## Enum Values

### valueRenderOption

| Value | Behavior |
|-------|----------|
| `FormattedValue` | Returns display string (default) |
| `UnformattedValue` | Returns raw value (numbers as numbers) |
| `Formula` | Returns formula string if cell has formula |
| `ToString` | Converts all values to string |

### dateTimeRenderOption

| Value | Behavior |
|-------|----------|
| `FormattedString` | Returns date/time as formatted display string |

### insertDataOption (append_data)

| Value | Behavior |
|-------|----------|
| `OVERWRITE` | Writes starting from first empty row found (default) |
| `INSERT_ROWS` | Inserts new rows, pushes existing data down |

### merge_type (merge_cells)

| Value | Behavior |
|-------|----------|
| `MERGE_ALL` | Merges entire range into one cell |
| `MERGE_ROWS` | Merges cells within each row independently |
| `MERGE_COLUMNS` | Merges cells within each column independently |

### major_dimension (insert_dimension / delete_dimension)

| Value | Behavior |
|-------|----------|
| `ROWS` | Operates on horizontal rows |
| `COLUMNS` | Operates on vertical columns |

### inherit_style (insert_dimension)

| Value | Behavior |
|-------|----------|
| `BEFORE` | Copies style from the row/column immediately before inserted range (default) |
| `AFTER` | Copies style from the row/column immediately after inserted range |

---

## Dimension Index Notes

- `start_index` and `end_index` are **0-based**
- `end_index` is **exclusive** (like Python slices)
- To insert 1 row before UI row 2: `start_index=1, end_index=2`
- To delete UI rows 3–5: `start_index=2, end_index=5`

---

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Read/write | ~100 QPS per app (TBD — Lark does not publish exact limits) |

**Retry strategy**: Exponential backoff — 2s, 4s, 8s. Built into `LarkAPIBase`.
On error code `1254290`, back off immediately before retry.

---

## Error Code Reference

| Code | HTTP | Meaning | Fix |
|------|------|---------|-----|
| 0 | 200 | Success | Continue |
| 190002 | 400 | Invalid parameters | Check field names, types, required fields |
| 190003 | 500 | Internal service error | Retry; contact support if persistent |
| 99991663 | 401 | Token expired | Call MCP `refresh_lark_token` |
| 99991664 | 403 | Permission denied | Check app has `sheets:spreadsheet` scope |
| 1254290 | 429 | Rate limited | Backoff (2s, 4s, 8s) then retry |

---

## find_cells condition Schema

```python
condition = {
    "match_case":        bool,   # case-sensitive search
    "match_entire_cell": bool,   # exact full-cell match only
    "regex":             bool,   # treat find string as regex
}
```

## operate_sheets Request Schemas

```python
# Add sheet
{"addSheet": {"properties": {"title": str, "index": int}}}

# Copy sheet within same spreadsheet
{"copySheet": {"source": sheet_id_str, "destination": {"title": str}}}

# Delete sheet
{"deleteSheet": {"sheetId": sheet_id_str}}

# Rename sheet
{"updateSheet": {"properties": {"sheetId": sheet_id_str, "title": str}}}
```
