# Lark Base Formula Functions Catalog

Quick lookup for all formula functions (~113 functions across 8 categories).
Compact catalog — each entry 3-5 lines max.

> Cross-table reference syntax `[OtherTable].[Field]` is the PREFERRED way to reference external data.
> Use FILTER/LOOKUP only when you need conditional filtering or dynamic matching.

---

## Quick Reference Table

| Function | Category | Syntax | Returns |
|---|---|---|---|
| ABS | Math | `ABS(number)` | Number |
| ACOS | Math | `ACOS(number)` | Number (radians) |
| ACOSH | Math | `ACOSH(number)` | Number |
| AND | Logical | `AND(expr1, [expr2, ...])` | Boolean |
| ARRAYJOIN | List | `ARRAYJOIN(list, [sep])` | Text |
| ASIN | Math | `ASIN(number)` | Number (radians) |
| ASINH | Math | `ASINH(number)` | Number |
| ATAN | Math | `ATAN(number)` | Number (radians) |
| ATAN2 | Math | `ATAN2(x, y)` | Number (radians) |
| ATANH | Math | `ATANH(number)` | Number |
| AVERAGE | Math | `AVERAGE(v1, [v2, ...])` | Number |
| CEILING | Math | `CEILING(value, [factor])` | Number |
| CHAR | Text | `CHAR(integer)` | Text |
| CONCATENATE | Text | `CONCATENATE(str1, [str2, ...])` | Text |
| CONTAIN | Logical | `CONTAIN(range, val1, ...)` | Boolean |
| CONTAINSALL | Logical | `CONTAINSALL(range, val1, ...)` | Boolean |
| CONTAINSONLY | Logical | `CONTAINSONLY(range, val1, ...)` | Boolean |
| CONTAINTEXT | Text | `CONTAINTEXT(text, find_text)` | Boolean |
| COS | Math | `COS(angle)` | Number |
| COSH | Math | `COSH(number)` | Number |
| COUNTA | Math | `COUNTA(v1, [v2, ...])` | Number |
| COUNTIF | Statistical | `range.COUNTIF(condition)` | Number |
| DATE | Date/Time | `DATE(year, month, day)` | Date |
| DATEDIF | Date/Time | `DATEDIF(start, end, unit)` | Number |
| DAY | Date/Time | `DAY(date)` | Number |
| DAYS | Date/Time | `DAYS(end, start)` | Number |
| DISTANCE | Position | `DISTANCE(loc1, loc2)` | Number (km) |
| DURATION | Date/Time | `DURATION(days, [hrs], [mins], [secs])` | Date offset |
| EDATE | Date/Time | `EDATE(start, months)` | Date |
| ENCODEURL | Text | `ENCODEURL(text)` | Text |
| EOMONTH | Date/Time | `EOMONTH(start, months)` | Date |
| FALSE | Logical | `FALSE()` | Boolean |
| FILTER | List | `range.FILTER(condition)` | Array |
| FIND | Text | `FIND(val, range, [start])` | Number |
| FIRST | List | `FIRST(list)` | Any |
| FLOOR | Math | `FLOOR(value, [factor])` | Number |
| FORMAT | Text | `FORMAT(template, [val, ...])` | Text |
| HOUR | Date/Time | `HOUR(time)` | Number |
| HYPERLINK | Text | `HYPERLINK(url, [text])` | Text |
| IF | Logical | `IF(cond, true_val, [false_val])` | Any |
| IFBLANK | Logical | `IFBLANK(value, default)` | Any |
| IFERROR | Logical | `IFERROR(value, [on_error])` | Any |
| IFS | Logical | `IFS(cond1, val1, [cond2, val2, ...])` | Any |
| INT | Math | `INT(number)` | Number |
| ISBLANK | Logical | `ISBLANK(value)` | Boolean |
| ISNULL | Logical | `ISNULL(value)` | Boolean |
| ISNUMBER | Logical | `ISNUMBER(value)` | Boolean |
| ISODD | Math | `ISODD(number)` | Boolean |
| ISERROR | Logical | `ISERROR(value)` | Boolean |
| LAST | List | `LAST(list)` | Any |
| LEFT | Text | `LEFT(str, [n])` | Text |
| LEN | Text | `LEN(text)` | Number |
| LIST | List | `LIST(v1, [v2, ...])` | Array |
| LISTCOMBINE | List | `LISTCOMBINE(field1, [field2, ...])` | Array |
| LOOKUP | List | `LOOKUP(val, match_field, result_field, [mode])` | Any |
| LOWER | Text | `LOWER(text)` | Text |
| MAP | List | `range.MAP(mapped_value)` | Array |
| MAX | Math | `MAX(v1, [v2, ...])` | Number |
| MEDIAN | Math | `MEDIAN(v1, [v2, ...])` | Number |
| MID | Text | `MID(str, start, length)` | Text |
| MIN | Math | `MIN(v1, [v2, ...])` | Number |
| MINUTE | Date/Time | `MINUTE(time)` | Number |
| MOD | Math | `MOD(dividend, divisor)` | Number |
| MONTH | Date/Time | `MONTH(date)` | Number |
| NETWORKDAYS | Date/Time | `NETWORKDAYS(start, end, [holidays])` | Number |
| NOT | Logical | `NOT(expr)` | Boolean |
| NOW | Date/Time | `NOW()` | DateTime |
| NTH | List | `list.NTH(position)` | Any |
| OR | Logical | `OR(expr1, [expr2, ...])` | Boolean |
| PI | Math | `PI()` | Number |
| POWER | Math | `POWER(base, exp)` | Number |
| QUOTIENT | Math | `QUOTIENT(dividend, divisor)` | Number |
| RANDOMBETWEEN | Logical | `RANDOMBETWEEN(min, max, [update])` | Number |
| RANDOMITEM | Logical | `RANDOMITEM(list, [update])` | Any |
| RANK | Logical | `RANK(value, range, [asc])` | Number |
| RECORD_ID | Logical | `RECORD_ID()` | Text |
| REGEXEXTRACT | Text | `REGEXEXTRACT(text, regex)` | Text |
| REGEXEXTRACTALL | Text | `REGEXEXTRACTALL(text, regex)` | Array |
| REGEXMATCH | Text | `REGEXMATCH(text, regex)` | Boolean |
| REGEXREPLACE | Text | `REGEXREPLACE(text, regex, replacement)` | Text |
| REPLACE | Text | `REPLACE(text, pos, len, new_text)` | Text |
| RIGHT | Text | `RIGHT(str, [n])` | Text |
| ROUND | Math | `ROUND(number, digits)` | Number |
| ROUNDDOWN | Math | `ROUNDDOWN(number, digits)` | Number |
| ROUNDUP | Math | `ROUNDUP(number, digits)` | Number |
| SECOND | Date/Time | `SECOND(time)` | Number |
| SEQUENCE | Math | `SEQUENCE(start, end, [step])` | Array |
| SIN | Math | `SIN(angle)` | Number |
| SINH | Math | `SINH(number)` | Number |
| SORT | List | `SORT(list, [asc])` | Array |
| SORTBY | List | `SORTBY(range, by_col, [asc]).result_col` | Array |
| SPLIT | Text | `SPLIT(text, separator)` | Array |
| SUBSTITUTE | Text | `SUBSTITUTE(text, old, new, [n])` | Text |
| SUM | Math | `SUM(v1, [v2, ...])` | Number |
| SUMIF | Statistical | `range.SUMIF(condition)` | Number |
| SWITCH | Logical | `SWITCH(expr, expr1, val1, [...], [default])` | Any |
| TAN | Math | `TAN(angle)` | Number |
| TANH | Math | `TANH(number)` | Number |
| TEXT | Text | `TEXT(value, format)` | Text |
| TODATE | Text | `TODATE(text)` | Date |
| TODAY | Date/Time | `TODAY()` | Date |
| TRIM | Text | `TRIM(text)` | Text |
| TRUE | Logical | `TRUE()` | Boolean |
| UNIQUE | List | `UNIQUE(v1, [v2, ...])` | Array |
| UPPER | Text | `UPPER(text)` | Text |
| VALUE | Math | `VALUE(text)` | Number |
| WEEKDAY | Date/Time | `WEEKDAY(date, [type])` | Number |
| WEEKNUM | Date/Time | `WEEKNUM(date, [type])` | Number |
| WORKDAY | Date/Time | `WORKDAY(start, days, [holidays])` | Date |
| YEAR | Date/Time | `YEAR(date)` | Number |

---

## Date & Time (18 functions)

### DATE
`DATE(year, month, day)` — Constructs a date from integers.
- Returns: Date
- Example: `DATE(2000,01,01)` → `2000/01/01`

### DATEDIF
`DATEDIF(start, end, unit)` — Days/months/years between two dates.
- **unit**: `"Y"` (years), `"M"` (months), `"D"` (days), `"MD"` (days ignoring months/years), `"YM"` (months ignoring years), `"YD"` (days ignoring years)
- Returns: Number
- Example: `DATEDIF([Start], [End], "D")` → days between

### DAY
`DAY(date)` — Extracts day integer from a date.
- Returns: Number (1-31)
- Example: `DAY("2000-01-03")` → `3`

### DAYS
`DAYS(end, start)` — Number of days between end and start date.
- Returns: Number
- Example: `DAYS("2000-01-08","2000-01-01")` → `7`

### DURATION
`DURATION(days, [hours], [minutes], [seconds])` — Creates a date offset for arithmetic.
- Returns: Duration value (use with `NOW()` or `TODAY()`)
- Example: `NOW()+DURATION(0,12)` → adds 12 hours to current time

### EDATE
`EDATE(start, months)` — Date N months before/after start. Negative months = past.
- Returns: Date
- Example: `EDATE("2011/01/31", 1)` → `2011/02/28` (last day of month)

### EOMONTH
`EOMONTH(start, months)` — Last day of the month N months from start.
- Returns: Date
- Example: `EOMONTH("2000-1-1", 1)` → `2000/2/28`

### HOUR / MINUTE / SECOND
`HOUR(time)` / `MINUTE(time)` / `SECOND(time)` — Extract time components.
- Returns: Number
- Example: `HOUR("11:40:59")` → `11`

### MONTH
`MONTH(date)` — Extracts month integer from a date.
- Returns: Number (1-12)
- Example: `MONTH("2000-12-01")` → `12`

### NETWORKDAYS
`NETWORKDAYS(start, end, [holidays])` — Working days between dates, excluding weekends.
- **holidays**: Optional date field or array of holiday dates
- Returns: Number (whole days only)
- Example: `NETWORKDAYS([Start], [End], [Holidays].[Date])`

### NOW
`NOW()` — Current date and time. Refreshes every 5 min while editing, every 30 min in automations.
- Returns: DateTime
- Example: `NOW()` → `2000/01/01 00:00`

### TODAY
`TODAY()` — Current date (no time).
- Returns: Date
- Example: `TODAY()`

### WEEKDAY
`WEEKDAY(date, [type])` — Day of week as integer. Type 1 = Sunday=1; Type 2 = Monday=1. Default: 1.
- Returns: Number (1-7)
- Example: `WEEKDAY("2000-01-01")` → `7`

### WEEKNUM
`WEEKNUM(date, [type])` — Week number in current year.
- Returns: Number
- Example: `WEEKNUM("2000-01-01")` → `1`

### WORKDAY
`WORKDAY(start, days, [holidays])` — End date after N working days from start.
- Returns: Date
- Example: `WORKDAY("2000/01/01", 7)` → `2000/01/11`

### YEAR
`YEAR(date)` — Extracts year integer from a date.
- Returns: Number
- Example: `YEAR("2000-01-01")` → `2000`

---

## Logical (23 functions)

### AND
`AND(expr1, [expr2, ...])` — TRUE only if all arguments are TRUE.
- Returns: Boolean
- Example: `AND([Score]>=60, [Attended]=TRUE)`

### CONTAIN
`CONTAIN(range, val1, [val2, ...])` — TRUE if range contains any of the specified values. Case-insensitive exact match.
- Note: Use CONTAINTEXT for substring matching.
- Returns: Boolean
- Example: `IF(CONTAIN([Region], "Japan", "Korea"), "APAC", "Other")`

### CONTAINSALL
`CONTAINSALL(range, val1, [val2, ...])` — TRUE if range contains ALL specified values.
- Returns: Boolean
- Example: `CONTAINSALL([Skills], "Python", "SQL")`

### CONTAINSONLY
`CONTAINSONLY(range, val1, [val2, ...])` — TRUE if range contains ONLY the specified values.
- Returns: Boolean
- Example: `IF([Answers].CONTAINSONLY("A","B","C"), "Correct", "Wrong")`

### FALSE / TRUE
`FALSE()` / `TRUE()` — Return literal boolean values.
- Returns: Boolean

### IF
`IF(cond, true_val, [false_val])` — Single condition branch.
- Returns: Any (matches true_val/false_val type)
- Example: `IF([Budget]-[Cost]<0, "Over", "Under")`

### IFBLANK
`IFBLANK(value, default)` — Returns value if not blank; otherwise returns default.
- Returns: Any
- Example: `IFBLANK([Owner], "Unassigned")`

### IFERROR
`IFERROR(value, [on_error])` — Returns value if no error; otherwise returns on_error.
- Returns: Any
- Example: `IFERROR([Revenue]/[Units], 0)`

### IFS
`IFS(cond1, val1, [cond2, val2, ...])` — Multi-condition branch; returns first matching value. Use `TRUE` as final catch-all condition.
- Returns: Any
- Example: `IFS([Score]>=80,"A",[Score]>=60,"B",TRUE,"F")`

### ISBLANK
`ISBLANK(value)` — TRUE if value is blank/empty.
- Returns: Boolean
- Example: `ISBLANK([Delivery date])`

### ISNULL
`ISNULL(value)` — TRUE if value is null/empty (alias for ISBLANK in most cases).
- Returns: Boolean

### ISNUMBER
`ISNUMBER(value)` — TRUE if value is numeric.
- Returns: Boolean
- Example: `ISNUMBER([Field])` → `TRUE` for numbers, `FALSE` for text

### ISERROR
`ISERROR(value)` — TRUE if value is an error (#VALUE!, #REF!, etc.).
- Returns: Boolean
- Example: `ISERROR(1/0)` → `TRUE`

### NOT
`NOT(expr)` — Inverts a boolean value.
- Returns: Boolean
- Example: `NOT(ISBLANK([Date]))`

### OR
`OR(expr1, [expr2, ...])` — TRUE if any argument is TRUE.
- Returns: Boolean
- Example: `OR([Status]="Active", [Status]="Pending")`

### RANDOMBETWEEN
`RANDOMBETWEEN(min, max, [update])` — Random integer between min and max. update=TRUE refreshes on each record change.
- Returns: Number
- Example: `RANDOMBETWEEN(1, 100)`

### RANDOMITEM
`RANDOMITEM(list, [update])` — Random item from a list.
- Returns: Any
- Example: `LIST("A","B","C").RANDOMITEM()`

### RANK
`RANK(value, range, [asc])` — Rank of value in range. asc=FALSE (default) = descending. Returns -1 if not found.
- Returns: Number
- Example: `RANK([Sales], [SalesTable].[Sales], FALSE)`

### RECORD_ID
`RECORD_ID()` — Unique ID of the current record row.
- Returns: Text
- Example: `RECORD_ID()`

### SWITCH
`SWITCH(expr, match1, val1, [match2, val2, ...], [default])` — Match expression against cases.
- Returns: Any
- Example: `SWITCH([Day], 1,"Mon", 2,"Tue", 3,"Wed", "Other")`

---

## Text (22 functions)

### CHAR
`CHAR(integer)` — Unicode character for integer code. Use `CHAR(10)` for newline.
- Returns: Text
- Example: `[Name] & CHAR(10) & [Dept]` (name + line break + dept)

### CONCATENATE
`CONCATENATE(str1, [str2, ...])` — Joins multiple strings. Prefer `&` operator for brevity.
- Returns: Text
- Example: `CONCATENATE("Hello", " ", [Name])`

### CONTAINTEXT
`CONTAINTEXT(text, find_text)` — TRUE if text contains find_text (substring match, case-insensitive).
- Returns: Boolean
- Example: `CONTAINTEXT([Notes], "urgent")`

### ENCODEURL
`ENCODEURL(text)` — URL-encodes text (replaces spaces and special chars).
- Returns: Text
- Example: `ENCODEURL("Base formula")` → `Base%20formula`

### FIND
`FIND(val, range, [start])` — Position of first occurrence (case-sensitive). Returns -1 if not found.
- Returns: Number
- Example: `FIND("@", [Email])` → position of @ sign

### FORMAT
`FORMAT(template, [val, ...])` — Fill template placeholders `{1}`, `{2}`, etc.
- Returns: Text
- Example: `FORMAT("{1} scored {2}", [Name], [Score])` → "Josh scored 95"

### HYPERLINK
`HYPERLINK(url, [display_text])` — Creates a clickable hyperlink in cell.
- Returns: Text (hyperlink)
- Example: `HYPERLINK([URL], [Title])`

### LEFT / RIGHT
`LEFT(str, [n])` / `RIGHT(str, [n])` — First/last N characters. Default n=1.
- Returns: Text
- Example: `LEFT([Email], FIND("@",[Email])-1)` → username before @

### LEN
`LEN(text)` — Character count of text.
- Returns: Number
- Example: `LEN([Description])`

### LOWER / UPPER
`LOWER(text)` / `UPPER(text)` — Convert case.
- Returns: Text
- Example: `UPPER([Code])`

### MID
`MID(str, start, length)` — Substring starting at position (1-indexed).
- Returns: Text
- Example: `MID([Phone], 1, 3)` → area code

### REGEXEXTRACT
`REGEXEXTRACT(text, regex)` — First regex match in text.
- Returns: Text
- Example: `REGEXEXTRACT([Bio], "\d{11}")` → 11-digit number

### REGEXEXTRACTALL
`REGEXEXTRACTALL(text, regex)` — All regex matches as array.
- Returns: Array
- Example: `REGEXEXTRACTALL([Text], "\d{11}")`

### REGEXMATCH
`REGEXMATCH(text, regex)` — TRUE if text matches regex pattern.
- Returns: Boolean
- Example: `REGEXMATCH([Phone], "^\d{11}$")`

### REGEXREPLACE
`REGEXREPLACE(text, regex, replacement)` — Replace all regex matches.
- Returns: Text
- Example: `REGEXREPLACE([Bio], "\d{11}", "***")` → mask phone numbers

### REPLACE
`REPLACE(text, pos, length, new_text)` — Replace by position (1-indexed).
- Returns: Text
- Example: `REPLACE("abcdefg", 1, 6, "xyz")` → `"xyzg"`

### SPLIT
`SPLIT(text, separator)` — Split text into array by separator.
- Returns: Array
- Example: `SPLIT("a,b,c", ",")` → `["a","b","c"]`

### SUBSTITUTE
`SUBSTITUTE(text, old, new, [n])` — Replace by value. n=1 replaces first occurrence only; omit to replace all.
- Returns: Text
- Example: `SUBSTITUTE([Tags], ",", " | ")`

### TEXT
`TEXT(value, format)` — Format number or date as text string.
- **format**: `"YYYY/MM/DD"`, `"MM/DD HH:MM"`, `"0.0%"`, `"[h]"` (hours), `"[m]"` (minutes)
- Returns: Text
- Example: `TEXT([Date], "YYYY/MM/DD")` | `TEXT([Duration], "[h]")`

### TODATE
`TODATE(text)` — Converts text to date type.
- Returns: Date
- Example: `TODATE("2023-6-5")` → `2023/06/05`

### TRIM
`TRIM(text)` — Remove leading, trailing, and duplicate spaces.
- Returns: Text
- Example: `TRIM([Name])`

---

## Math (35 functions)

### ABS
`ABS(number)` — Absolute value.
- Example: `ABS(-5)` → `5`

### ACOS / ASIN / ATAN / ATAN2
Trigonometric inverses in radians. `ATAN2(x,y)` returns arctangent of y/x.
- Example: `ACOS(-0.5)*180/PI()` → `120` (degrees)

### ACOSH / ASINH / ATANH
Inverse hyperbolic functions.
- Example: `ACOSH(1)` → `0`

### AVERAGE
`AVERAGE(v1, [v2, ...])` — Arithmetic mean.
- Example: `AVERAGE([Q1],[Q2],[Q3],[Q4])`

### CEILING
`CEILING(value, [factor])` — Round up to nearest factor multiple. Default factor=1.
- Example: `CEILING(3.21, 0.2)` → `3.4`

### COS / SIN / TAN
Trigonometric functions in radians.
- Example: `COS(60*PI()/180)` → `0.5`

### COSH / SINH / TANH
Hyperbolic functions.
- Example: `TANH(0)` → `0`

### COUNTA
`COUNTA(v1, [v2, ...])` — Count non-blank values.
- Example: `COUNTA([Attachments])` → number of attachments

### FLOOR
`FLOOR(value, [factor])` — Round down to nearest factor multiple. Default factor=1.
- Example: `FLOOR(3.14, 0.1)` → `3.1`

### INT
`INT(number)` — Truncate to integer (round toward negative infinity).
- Example: `INT(8.9)` → `8`, `INT(-8.9)` → `-9`

### ISODD
`ISODD(number)` — TRUE if number is odd.
- Example: `ISODD(3)` → `TRUE`

### MAX / MIN
`MAX(v1, [v2, ...])` / `MIN(v1, [v2, ...])` — Maximum/minimum of values or field.
- Example: `MAX([TeamA].[Sales], [TeamB].[Sales])` — max across two table columns

### MEDIAN
`MEDIAN(v1, [v2, ...])` — Median of values. Arrays count as single argument.
- Example: `MEDIAN([Scores].[Value])`

### MOD
`MOD(dividend, divisor)` — Remainder of division.
- Example: `MOD([Row], 2)` → alternating 0/1 for even/odd rows

### PI
`PI()` — Mathematical constant π (3.14159...).
- Example: `2*PI()*[Radius]`

### POWER
`POWER(base, exp)` — base raised to exp.
- Example: `POWER([Side], 2)` → area of square

### QUOTIENT
`QUOTIENT(dividend, divisor)` — Integer portion of division (drops remainder).
- Example: `QUOTIENT(5, 2)` → `2`

### ROUND / ROUNDUP / ROUNDDOWN
Round to N digits. digits>0=decimal places; digits=0=whole; digits<0=before decimal.
- Example: `ROUND([Price], 2)` → 2 decimal places

### SEQUENCE
`SEQUENCE(start, end, [step])` — Array of sequential numbers. Default step=1.
- Returns: Array
- Example: `SEQUENCE(1, 10, 2)` → `[1,3,5,7,9]`

### SUM
`SUM(v1, [v2, ...])` — Sum of values or field.
- Example: `SUM([Q1],[Q2],[Q3])` or `[Table].[Revenue].SUM()`

### VALUE
`VALUE(text)` — Convert text (with currency/date/time format) to number.
- Example: `VALUE("$50")` → `50`

---

## Statistical (3 functions)

> Prefer `[OtherTable].[Field].SUM()` or `.MAX()` for simple aggregation over SUMIF/COUNTIF when no filtering needed.

### COUNTIF
`range.COUNTIF(condition)` — Count values in range matching condition. Uses `CurrentValue` to reference each element.
- **Limitation**: Cannot use multi-value fields (Person, Group, Multi-select) as range.
- Returns: Number
- Example: `[Sales].COUNTIF(CurrentValue>[Target])` — count rows exceeding target
- Example: `[Table].COUNTIF(CurrentValue.[Score]>=80)` — count from whole table

### SUMIF
`range.SUMIF(condition)` — Sum values in range matching condition. Uses `CurrentValue`.
- Returns: Number
- Example: `[Sales].[Revenue].SUMIF(CurrentValue>1000)` — sum revenues over 1000
- Note: For per-member totals, use FILTER+SUM (preferred): `[Table].FILTER(CurrentValue.[Name]=[Name]).[Revenue].SUM()`

### FILTER (Statistical use)
`range.FILTER(condition).[field].aggregation()` — Conditional query pattern. Combines with SUM/COUNTA/MAX/etc.
- Uses `CurrentValue` for row iteration; `CurrentValue.[Field]` when range is a table.
- Example: `[Sales].FILTER(CurrentValue.[Month]=[Month]).[Revenue].SUM()`

---

## List & Array (11 functions)

> Use `[OtherTable].[Field]` to get all values from another table's field directly (no FILTER needed for simple references).

### ARRAYJOIN
`ARRAYJOIN(list, [sep])` — Join array into text string. Default separator is comma.
- Returns: Text
- Example: `ARRAYJOIN([Tags], " | ")`

### FILTER
`range.FILTER(condition)` — Filter records by condition. Must chain `.field` to get values.
- Returns: Array
- Example: `[Orders].FILTER(CurrentValue.[Status]="Open").[Amount]`

### FIRST / LAST
`FIRST(list)` / `LAST(list)` — First/last element of array.
- Example: `[Sales].FILTER(...).[Date].SORT().FIRST()` → earliest date

### LIST
`LIST(v1, [v2, ...])` — Creates an array from multiple values or fields.
- Returns: Array
- Example: `LIST([Q1],[Q2],[Q3],[Q4])` → array of four values

### LISTCOMBINE
`LISTCOMBINE(field1, [field2, ...])` — Concatenates multiple arrays (keeps duplicates).
- Returns: Array
- Example: `[Tags1].LISTCOMBINE([Tags2])` → merged tag list

### LOOKUP
`LOOKUP(val, match_field, result_field, [mode])` — Find val in match_field, return result_field.
- **mode**: `1` = split (multi-select split to singles), `0` = integrated (multi-select as array)
- Returns: Any
- Note: Prefer `[OtherTable].[Field]` cross-table reference when no matching logic needed.
- Example: `LOOKUP([Name], [Sales].[Name], [Sales].[Revenue])`

### MAP
`range.MAP(mapped_value)` — Transform each element. Uses `CurrentValue`. No nesting allowed.
- Returns: Array
- Example: `[Prices].MAP(CurrentValue * 1.1)` → 10% price increase

### NTH
`list.NTH(position)` — Element at 1-indexed position.
- Returns: Any
- Example: `LIST(1,3,5,7).NTH(2)` → `3`

### SORT
`SORT(list, [asc])` — Sort numeric array. asc=TRUE (default) = ascending.
- Returns: Array (numbers only)
- Example: `[Scores].SORT(FALSE)` → descending

### SORTBY
`SORTBY(range, by_col, [asc]).result_col` — Sort records by a field, return another field.
- Returns: Array
- Example: `[Sales].SORTBY([Sales].[Date]).[Amount]` → amounts sorted by date

### UNIQUE
`UNIQUE(v1, [v2, ...])` — Deduplicated array. Output order is not guaranteed.
- Returns: Array
- Example: `UNIQUE([Category])` → distinct categories

---

## Position (1 function)

### DISTANCE
`DISTANCE(loc1, loc2)` — Straight-line distance between two location fields (km by default).
- Returns: Number
- Example: `DISTANCE([Office], [Home])` → commute distance in km
