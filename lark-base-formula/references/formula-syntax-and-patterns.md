# Formula Syntax & Patterns

Syntax rules, field reference patterns, and common formula recipes.

> **KEY PRINCIPLE**: Always prefer `[OtherTable].[Field]` cross-table references over LOOKUP/FILTER
> when simply reading another table's data. It's simpler, faster, and more readable.

---

## Field Reference Syntax

| Pattern | What It References | Example |
|---|---|---|
| `[Field]` | Current row's value in Field | `[Revenue]` → this row's revenue |
| `[Table].[Field]` | ALL values in Field from Table (same base) | `[Sales].[Revenue]` → all revenues |
| `[OtherTable].[Field]` | ALL values in another table's field | `[Products].[Price]` → all prices |
| `CurrentValue` | Current element during FILTER/SUMIF/COUNTIF iteration | `CurrentValue.[Score]` |
| `@CurrentValue` | Alias for CurrentValue (both work identically) | `@CurrentValue > 100` |
| `"text"` | String literal (English double quotes only) | `"Open"`, `"2024-01-01"` |
| `123` / `0.15` | Number literal | `[Price] * 1.15` |
| `TRUE` / `FALSE` | Boolean literal | `IF([Done]=TRUE, ...)` |

---

## Operators

### Arithmetic
| Op | Meaning | Example |
|---|---|---|
| `+` | Add | `[Price] + [Tax]` |
| `-` | Subtract | `[Revenue] - [Cost]` |
| `*` | Multiply | `[Qty] * [UnitPrice]` |
| `/` | Divide | `[Total] / [Count]` |
| `%` | Modulo | `MOD([Row], 2)` |

### Comparison
| Op | Meaning | Example |
|---|---|---|
| `=` | Equal | `[Status] = "Open"` |
| `!=` | Not equal | `[Status] != "Closed"` |
| `>` / `>=` | Greater than | `[Score] >= 80` |
| `<` / `<=` | Less than | `[Date] < TODAY()` |

### Logical
| Op | Meaning | Example |
|---|---|---|
| `&&` | AND | `[Score]>=60 && [Attended]=TRUE` |
| `\|\|` | OR | `[Status]="Open" \|\| [Status]="Pending"` |

### String
| Op | Meaning | Example |
|---|---|---|
| `&` | Concatenate | `[First] & " " & [Last]` |

---

## Cross-Table References (PREFERRED APPROACH)

**Why preferred over FILTER/LOOKUP:**
- Simpler syntax — no CurrentValue needed
- Faster — server-optimized direct field reference
- More readable — intent is immediately clear
- Less error-prone — no condition logic to get wrong

### Syntax
```
[TableName].[FieldName]
```
This returns ALL values in FieldName from TableName as an array.
Chain aggregation directly: `.SUM()`, `.MAX()`, `.MIN()`, `.COUNTA()`

### Examples

**Simple aggregation (cross-table preferred):**
```
// Total of all revenue from another table
SUM([SalesData].[Revenue])

// Max sales amount across all records
MAX([SalesData].[Amount])

// Count all entries in another table
COUNTA([Orders].[ID])

// Proportion: this row's sales vs total
[Sales] / SUM([Team].[Sales])
```

**Difference from cross-table max:**
```
// Difference between current row and highest value in another table
MAX([TeamB].[ComputerSales]) - [ComputerSales]
```

**Multi-table aggregation:**
```
// Compare two teams' max values
MAX([TeamA].[Revenue]) - MAX([TeamB].[Revenue])
```

---

## When FILTER Is Still Needed

Use FILTER only when you need **conditional row-level filtering** (not just reading all values):

| Scenario | Use |
|---|---|
| Read all values from another table | `[Table].[Field]` (preferred) |
| Read values matching a condition | `[Table].FILTER(condition).[Field]` |
| Running total (rows up to current) | `[Table].FILTER(CurrentValue.[No]<=[No]).[Field].SUM()` |
| Per-member aggregation | `[Table].FILTER(CurrentValue.[Name]=[Name]).[Field].SUM()` |
| Month-over-month comparison | `[Table].FILTER(CurrentValue.[Month]=[Month]-1).[Field]` |

### FILTER pattern (when needed)
```
[TableName].FILTER(CurrentValue.[FieldA] = [FieldB]).[ResultField].SUM()
```

**Preferred FILTER format for performance:**
```
[Table].FILTER(
  CurrentValue.[Field] = constant_or_field &&
  CurrentValue.[Field2] >= value
)
.[ResultField]
.SUM()  // or .COUNTA(), .MAX(), .ARRAYJOIN(), etc.
```

---

## When LOOKUP Is Needed

LOOKUP is for **dynamic matching with mode control** (especially multi-select fields):

```
LOOKUP([Name], [Sales].[Name], [Sales].[Revenue])
```

- `mode=1` (default): split — treats multi-select as individual values
- `mode=0`: integrated — treats multi-select as array

Use LOOKUP when:
- Matching against multi-select fields with split/integrate control
- Single point lookup without aggregation needed
- Dynamic field matching from user input

---

## CurrentValue Usage

`CurrentValue` is a special argument for statistical functions. It represents each element as the function iterates through the range.

### Two contexts

**1. Table as range** — CurrentValue = each row:
```
// Returns all rows where Score > 80
[Table].FILTER(CurrentValue.[Score] > 80).[Name]

// Count rows where Status is "Done"
[Table].COUNTIF(CurrentValue.[Status] = "Done")
```

**2. Field as range** — CurrentValue = each cell value:
```
// Returns only values > 80 from the Score field
[Score].FILTER(CurrentValue > 80)

// Sum only values over 1000
[Revenue].SUMIF(CurrentValue > 1000)
```

### CurrentValue vs @CurrentValue
Both are identical. `@CurrentValue` is just an alias:
```
[Table].FILTER(CurrentValue.[Score] > 80)
// same as:
[Table].FILTER(@CurrentValue.[Score] > 80)
```

---

## Common Formula Patterns

### 1. Running Total
Accumulate values in rows up to current row (requires a row number field `[No.]`):
```
[CurrentTable].FILTER(CurrentValue.[No.] <= [No.]).[Amount].SUM()
```

### 2. Ranking
Rank current row's value among all rows:
```
[CurrentTable].FILTER(CurrentValue.[Sales] > [Sales]).[Name].COUNTA() + 1
```
Or using RANK function:
```
RANK([Sales], [CurrentTable].[Sales], FALSE)
```

### 3. Month-over-Month Growth
Compare current month to previous month (requires `[Month]` as integer 1-12):
```
([Amount] - [Table].FILTER(CurrentValue.[Month] = [Month]-1).[Amount]) /
[Table].FILTER(CurrentValue.[Month] = [Month]-1).[Amount]
```
Set the formula field format to Percentage.

### 4. Conditional Aggregation (cross-table preferred)
Sum per person across all records (FILTER approach):
```
[Sales].FILTER(CurrentValue.[Person] = [Name]).[Revenue].SUM()
```
Simple total without filtering (cross-table direct):
```
SUM([Sales].[Revenue])
```

### 5. Time Difference Calculations
Days between dates (simple subtraction):
```
[EndDate] - [StartDate]
```
Time difference in hours/minutes/seconds (as text):
```
TEXT([End] - [Start], "[h]")    // hours
TEXT([End] - [Start], "[m]")    // minutes
TEXT([End] - [Start], "[s]")    // seconds
```
Days/months/years (DATEDIF):
```
DATEDIF([Start], [End], "D")   // days
DATEDIF([Start], [End], "M")   // complete months
DATEDIF([Start], [End], "Y")   // complete years
```

### 6. Duplicate Detection
Mark duplicate values in a field:
```
IF([Name].COUNTIF(CurrentValue = [Name]) > 1, "Duplicate", "")
```

### 7. Text Extraction
Email username (before @):
```
LEFT([Email], FIND("@", [Email]) - 1)
```
Email domain (after @):
```
MID([Email], FIND("@", [Email]) + 1, LEN([Email]))
```
Format order code from date:
```
TEXT([Date], "YYMMDD") & "-" & [OrderID]
```

### 8. Multi-Condition Branching
Grade assignment:
```
IFS([Score]>=90,"A", [Score]>=80,"B", [Score]>=70,"C", [Score]>=60,"D", TRUE,"F")
```
Status with multiple fields:
```
IFS(
  ISBLANK([Start]), "Not started",
  ISBLANK([End]), "In progress",
  [End] < TODAY(), "Overdue",
  TRUE, "Completed"
)
```

### 9. Array Merge & Dedup
Combine tags from two fields and deduplicate:
```
UNIQUE([Tags1].LISTCOMBINE([Tags2]))
```
Join array to text:
```
ARRAYJOIN(UNIQUE([Tags]), ", ")
```

### 10. Working Days Calculation
Working days between two dates (excludes weekends):
```
NETWORKDAYS([StartDate], [EndDate])
```
With holidays from another table:
```
NETWORKDAYS([Start], [End], [Holidays].[Date])
```
Target end date after N working days:
```
WORKDAY([StartDate], 10)
```

### 11. Multi-Field Validation (LIST + COUNTIF)
Check all inspection fields pass:
```
// Step 1: Combine results into a list
LIST([Check1], [Check2], [Check3])

// Step 2: Count passes
IFS(
  [Status].COUNTIF(CurrentValue="Pass") = 3, "Qualified",
  [Status].COUNTIF(CurrentValue="") = 3, "Pending",
  TRUE, "Failed"
)
```

### 12. Date Construction from Parts
Add 2 months to a date:
```
DATE(YEAR([Start]), MONTH([Start]) + 2, DAY([Start]))
```
Add 1 year:
```
DATE(YEAR([Start]) + 1, MONTH([Start]), DAY([Start]))
```

### 13. Format date + text in one cell
```
TEXT([PurchaseDate], "YYYY/MM/DD") & " - " & [StockLevel] & " units"
```

---

## Data Type Conversions

| From | To | Function | Example |
|---|---|---|---|
| Text → Date | Date | `TODATE(text)` | `TODATE("2023-6-5")` |
| Text → Number | Number | `VALUE(text)` | `VALUE("$50")` → `50` |
| Number/Date → Text | Text | `TEXT(val, fmt)` | `TEXT([Date], "YYYY/MM/DD")` |
| Date → components | Number | `YEAR/MONTH/DAY(date)` | `YEAR([Date])` |
| Integer components → Date | Date | `DATE(y, m, d)` | `DATE(2024, 1, 1)` |
| Array → Text | Text | `ARRAYJOIN(arr, sep)` | `ARRAYJOIN([Tags], ", ")` |
| Text → Array | Array | `SPLIT(text, sep)` | `SPLIT([CSV], ",")` |

### Notes on TEXT with dates in arrays
When dates are inside a LIST(), wrap each with TEXT() to prevent serial number conversion:
```
// Wrong — date becomes serial number
ARRAYJOIN(LIST([Date1], [Date2]), ", ")

// Correct
ARRAYJOIN(LIST(TEXT([Date1],"YYYY/MM/DD"), TEXT([Date2],"YYYY/MM/DD")), ", ")
```

---

## Formula Field Constraints

- Formula applies to **entire field** (all rows share same formula, cannot differ per row)
- Only formula fields support formula input
- Text literals must use **English double quotes** (`"`) not curly/smart quotes
- Percentage values: use decimal (`0.10` = 10%), not `10%`
- Max 100 formula fields per table (300 fields total)
- Formula field is read-only at record level (calculated, not manually editable)
