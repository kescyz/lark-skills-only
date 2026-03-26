# Formula Errors & Limits

Error types, overflow limits, function gotchas, and optimization tips.

---

## Error Types

| Error | Cause | Common Trigger | Fix |
|---|---|---|---|
| `#N/A` | Missing data | LOOKUP finds no match | `IFERROR(formula, "")` |
| `#VALUE!` | Wrong type or invalid argument | Text in numeric field, invalid date, EDATE with empty arg | Check field types; use `VALUE()` or `TODATE()` to convert |
| `#REF!` | Reference to deleted/renamed field or table | Field renamed after formula created | Update formula to use new field name |
| `#DIV/0!` | Division by zero | `[Revenue]/[Count]` when Count=0 | `IFERROR([Revenue]/[Count], 0)` |
| `#NUM!` | Numeric calculation error | DATEDIF start > end; DATEDIF date before 1900 | Validate date range with IF before DATEDIF |
| `#NAME?` | Unrecognized function or field name | Typo in function name; field renamed | Check spelling; refresh formula editor |
| `#NULL!` | Incorrect range or empty intermediate result | Wrong operator; reference to empty field chain | Verify operator and field chain is non-null |
| `#ERROR!` | Runtime formula error | MAP nested inside MAP; unsupported operation | See function-specific gotchas below |

### Wrapping errors safely
```
IFERROR([Revenue] / [Units], 0)           // division safe
IFERROR(DATEDIF([Start],[End],"D"), "")   // date safe
IF(ISBLANK([Field]), "", formula)          // blank-safe before formula
```

---

## Overflow Limits

| Limit | Value | Affected Functions | Solution |
|---|---|---|---|
| Array elements per level | 200 | Any function returning array | Reduce FILTER conditions to narrow results |
| FILTER result rows | 20,000 | FILTER | Add more conditions; filter before aggregation |
| String intermediate size | 1 MB | CONCATENATE, REGEXREPLACE, ARRAYJOIN | Split into smaller steps; avoid full-table ARRAYJOIN |
| Function arguments | 5,000 | ARRAYJOIN, CONCATENATE, UNIQUE, SORT | Reduce input size |
| Cell result size | 4 MB | Any | Break complex formula into multiple fields |
| Field result size | 100 MB | Any field-level aggregation | Simplify formula; reduce data size returned |
| Table result size | 256 MB | Any formula field in table | Break calculations into steps; use multiple fields |
| Table storage | 10 GB | Entire table | Delete/archive data or split tables |
| Formula fields per table | 100 | — | Consolidate logic; use intermediate fields |
| Total fields per table | 300 | — | — |
| Field references per formula | 300 | — | Simplify formula; avoid referencing hundreds of fields |

---

## Function-Specific Gotchas

### COUNTIF
- Cannot use multi-value fields as range: Person, Group, Multi-select → use LISTCOMBINE workaround
- Workaround: `LISTCOMBINE([PersonField]).COUNTIF(CurrentValue = "John")`
- SUMIFS and COUNTIFS (with S) are **not supported** — use FILTER+SUM/COUNTA instead

### DATEDIF
- Start date must be after year 1900; earlier dates return `#NUM!`
- End date must be later than start date; reversed order returns `#NUM!`
- Validate: `IF([Start]<[End], DATEDIF([Start],[End],"D"), 0)`

### EDATE / EOMONTH
- If any argument cannot convert to date: returns `#VALUE!`
- If any argument is empty: returns `#VALUE!`
- Month overflow: `EDATE("2011/01/31", 1)` → `2011/02/28` (last day, not error)

### MAP
- No nesting allowed — `MAP` inside `MAP` returns `#ERROR!`
- Workaround: chain FILTER then MAP, or use intermediate formula field
- Valid: `[Table].FILTER(condition).[Field].MAP(CurrentValue * 1.1)`

### TEXT
- Dates inside LIST() must be wrapped in TEXT() — otherwise converts to serial number
- Wrong: `ARRAYJOIN(LIST([Date1], [Date2]), ", ")`
- Correct: `ARRAYJOIN(LIST(TEXT([Date1],"YYYY/MM/DD"), TEXT([Date2],"YYYY/MM/DD")), ", ")`
- Percentage format: use `"0.0%"` (TEXT formats the decimal as percentage display)

### FIND
- Case-sensitive — `FIND("a", "ABC")` returns `-1` (not found)
- Returns `-1` on miss, not an error — check with `IF(FIND(...)=-1, ...)`
- Use CONTAINTEXT for case-insensitive substring check

### UNIQUE
- Output order is not guaranteed (unsorted)
- If sorted output needed: chain with SORT — `SORT(UNIQUE([Field]))`
- To parse unique output: use "Text Split into Columns" extension

### FILTER
- Condition is required — cannot call `[Table].FILTER()` with no condition
- Must chain a field after FILTER to get values: `[Table].FILTER(...).[Field]`
- Cannot return more than 20,000 rows (overflow error)

### NETWORKDAYS
- Returns whole numbers only — fractional days are not possible
- Weekend = Saturday + Sunday (fixed; cannot redefine to Fri-Sat)
- Holidays arg must be a date field or date array, not a text string

### SUMIF / COUNTIF (field-as-range syntax)
- `[Field].SUMIF(CurrentValue > X)` sums/counts only the matching field column
- For per-member aggregation use FILTER+SUM: `[T].FILTER(CurrentValue.[Name]=[Name]).[Rev].SUM()`

### RANK
- Returns `-1` if value not found in search range
- Duplicate values receive the same rank (no tiebreaking)

### REGEXREPLACE
- Intermediate results exceeding 1 MB cause overflow error
- Avoid applying to very long text fields across all rows

### NOW / TODAY
- `NOW()` refreshes every 5 min while editing; every 30 min in automations/workflows
- Do not use NOW/TODAY in formulas that need stable historical values

---

## Optimization Tips

### Tip 1: Filter early — reduce data before aggregating
```
// Slow: scans everything, then sums
[SalesData].[Revenue].SUMIF(CurrentValue > 1000)

// Faster: filter first, then aggregate
[SalesData].FILTER(CurrentValue.[Revenue] > 1000).[Revenue].SUM()
```

### Tip 2: Use direct cross-table reference instead of FILTER when no condition needed
```
// Unnecessary FILTER
[Products].FILTER(TRUE).[Price].MAX()

// Preferred: direct reference
MAX([Products].[Price])
```

### Tip 3: Avoid fuzzy/text matching in FILTER conditions
```
// Performance risk: scans every row for text match
[Feedback].FILTER(CurrentValue.[Notes].CONTAINTEXT([Keyword])).[Count].COUNTA()

// Better: add a pre-classified label field, filter by exact match
[Feedback].FILTER(CurrentValue.[Label] = [Keyword]).[Count].COUNTA()
```

### Tip 4: Simplify nesting — follow flat chain pattern
```
// Preferred flat chain
[Table].FILTER(CurrentValue.[Field] = [Value]).[ResultField].SUM()

// Avoid deep nesting: IF(FILTER(IF(FILTER(...))))
```

### Tip 5: Use intermediate fields to store sub-results
```
// Instead of one giant formula, break into steps:
// Field A: [Revenue] - [Cost]           → margin
// Field B: [Margin] / [Revenue]         → margin %
// Field C: RANK([MarginPct], [T].[MarginPct], FALSE)  → rank
```

### Tip 6: Use Performance Diagnostics tool
- Click Base AI Q&A icon → Performance Diagnostics
- Identifies suboptimal FILTER, COUNTIF, SUMIF formulas
- Shows formulas with slow queries and long calculations
- Available to users with edit permission

---

## Formula Field Constraints

| Constraint | Detail |
|---|---|
| Scope | Formula applies to entire field — same formula for all rows, cannot vary per row |
| Max formula fields | 100 per table |
| Max total fields | 300 per table |
| Edit mode | Formula field is read-only (calculated); cannot manually enter cell values |
| Type change | Converting formula field to another type retains current values but loses formula |
| String literals | Must use English double quotes `"` — smart/curly quotes cause `#NAME?` error |
| Percentage values | Use decimal: `0.10` (not `10%`) — format the field to Percentage display |
| SUMIFS / COUNTIFS | Not supported — use FILTER + SUM/COUNTA instead |
| Circular reference | Formula cannot reference its own field |
| Cross-base reference | Cannot reference fields from a different Base (only same Base, any table) |
