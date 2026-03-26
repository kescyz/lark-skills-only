---
name: lark-base-formula
description: Lark Base formula reference - 100+ functions, cross-table patterns, syntax, errors. Use when user asks about Bitable formulas or calculated fields. Requires lark-token-manager MCP.
---

# Lark Base Formula Reference

Knowledge-only skill for writing and debugging Lark Base (Bitable) formulas. Covers 100+ functions across 8 categories, cross-table reference patterns, error handling, and optimization tips.

**No API calls, no tokens.** For creating/updating formula fields via API, use the `lark-base` skill.

## Encoding (Non-ASCII Data)

ALWAYS use the Python scripts (`scripts/`) for ALL API calls. NEVER use `curl` in Bash for requests containing non-ASCII characters (Vietnamese, Chinese, Japanese, etc.). Windows terminal encoding (cp1252) corrupts UTF-8 data, causing mojibake. The Python scripts use `urllib.request` with proper `ensure_ascii=False` encoding - this is the correct and safe approach.

## Formula Syntax Quick Reference

| Pattern | Scope | Example |
|---------|-------|---------|
| `[Field]` | Current record field | `[Revenue]` |
| `[Table].[Field]` | Cross-table reference (all rows) | `[Orders].[Amount]` |
| `CurrentValue` | Iterator in FILTER/SUMIF/COUNTIF | `CurrentValue.[Status]` |
| `"text"` | String literal (English double quotes only) | `"completed"` |
| `&&` / `\|\|` | Logical AND / OR | `[A]>0 && [B]>0` |
| `&` | Text concatenation | `[First] & " " & [Last]` |

## Function Categories

| Category | Count | Key Functions |
|----------|-------|---------------|
| Math | 35 | SUM, AVERAGE, MAX, MIN, ROUND, ABS, MOD, POWER |
| Text | 22 | CONCATENATE, LEFT, RIGHT, MID, FIND, TEXT, UPPER, LOWER, TRIM |
| Date | 18 | DATEDIF, NETWORKDAYS, NOW, TODAY, EDATE, YEAR, MONTH, DAY |
| Logical | 23 | IF, IFS, AND, OR, ISBLANK, IFBLANK, ISERROR, IFERROR, CONTAIN |
| Array | 11 | LIST, ARRAYJOIN, FILTER, SORT, UNIQUE, MAP, FIRST, LAST |
| Statistical | 3 | COUNTIF, SUMIF, FILTER (with CurrentValue) |
| Lookup | 1 | LOOKUP |
| Position | 1 | DISTANCE |

Full catalog: [formula-functions-catalog.md](./references/formula-functions-catalog.md)

## Cross-Table References (PREFERRED)

**Always prefer `[Table].[Field]` syntax over LOOKUP/FILTER when possible.**

```
# PREFERRED: Direct cross-table aggregation
[Orders].[Amount].SUM()

# PREFERRED: Cross-table with condition
[Orders].FILTER(CurrentValue.[Customer]=[Name]).[Amount].SUM()

# AVOID when direct ref works:
LOOKUP([ID], [Orders].[CustomerID], [Orders].[Amount])
```

**When to use LOOKUP/FILTER instead:**
- Complex conditional joins needing multiple conditions
- Dynamic field selection based on another field's value
- Split-mode lookups across linked records

## CurrentValue Usage

Used in FILTER, SUMIF, COUNTIF to iterate over rows:

```
[Sales].FILTER(CurrentValue.[Region]="Asia" && CurrentValue.[Amount]>1000)
[Sales].SUMIF(CurrentValue.[Status]="Closed")
[Sales].COUNTIF(CurrentValue.[Score]>80)
```

Both `CurrentValue` and `@CurrentValue` are valid.

## Common Patterns

```
# Conditional: IF([Budget]-[Cost]<0, "over budget", "under budget")
# Ranking: [Table].FILTER(CurrentValue.[Value]>[Value]).[Name].COUNTA()+1
# Time diff: DATEDIF([Start], [End], "D")
# Email user: LEFT([Email], FIND("@", [Email])-1)
# Dedup: UNIQUE([Products])
```

## Error Quick Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `#N/A` | Missing data | Check field exists, not blank |
| `#VALUE!` | Wrong type / syntax | Check quotes, operators |
| `#REF!` | Deleted field/table | Restore or update reference |
| `#DIV/0!` | Division by zero | Wrap with `IF([B]!=0, [A]/[B], 0)` |
| `#NUM!` | Numeric overflow | Check DATEDIF date range (>1900) |
| `#NAME?` | Unknown function | Check spelling, case |
| `#NULL!` | Bad range operator | Check syntax |

## References

- [Formula Functions Catalog](./references/formula-functions-catalog.md) — All 100+ functions with syntax
- [Formula Syntax & Patterns](./references/formula-syntax-and-patterns.md) — Cross-table refs, CurrentValue, operators
- [Formula Errors & Limits](./references/formula-errors-and-limits.md) — Error types, overflow limits, optimization