# Code Review: lark-sheets Plugin Implementation

## Scope
- Files: `lark_api.py` (164 LOC), `utils.py` (51 LOC), `test_e2e_live_api.py` (362 LOC), `SKILL.md` (153 lines)
- Focus: New plugin — API correctness, pattern compliance, test coverage, SKILL.md quality

## Overall Assessment

Solid implementation. Follows established LarkAPIBase patterns well. 17 methods correctly split across v2/v3 endpoints. SKILL.md is comprehensive. One critical bug in `batch_read_ranges`, one missing test.

---

## Critical Issues

### 1. `batch_read_ranges` — list params broken by `urlencode`

**File**: `lark_api.py:70`

`batch_read_ranges` passes `ranges` (a Python list) in `params` dict. `_call_api` uses `urlencode(params)` which serializes the list as its repr string (`%5B%27...%27%5D`) instead of repeated query params (`ranges=X&ranges=Y`).

**Impact**: `batch_read_ranges` will send malformed URL to Lark API — runtime failure on every call.

**Root cause**: `lark_api_base.py` uses `urlencode` without `doseq=True`. This is a shared-base limitation that no other skill has triggered until now (no other skill passes list params).

**Fix options** (pick one):
- **(A) Fix in `lark_api_base.py`**: Change line 47 to `urlencode(params, doseq=True)` — safe for all existing skills since `doseq` is backward-compatible with scalar values.
- **(B) Fix locally in `batch_read_ranges`**: Pre-join the ranges into a comma-separated string if Lark supports it, or manually build the query string.

**Recommended**: Option A — fixes systemically. Apply across all skill copies of `lark_api_base.py` and the template.

---

## High Priority

### 2. `batch_write_ranges` not tested in E2E

**File**: `test_e2e_live_api.py`

The docstring claims "Tests all 17 Sheets methods" but `batch_write_ranges` is never called. Only 16 of 17 methods are tested. The test list (lines 319-343) covers `write_range`, `read_range`, `append_data`, `batch_read_ranges` but skips `batch_write_ranges`.

**Fix**: Add a `test_XX_batch_write_ranges` between `test_11_batch_read_ranges` and `test_12_find_cells`. Write to two non-overlapping ranges on `new_sheet_id`, then verify with `batch_read_ranges`. Update docstring header accordingly.

### 3. `batch_read_ranges` test will fail (consequence of #1)

Even after adding it, `test_11_batch_read_ranges` will fail at runtime due to the urlencode bug above. Fix #1 first, then this test becomes meaningful.

---

## Medium Priority

### 4. Typo: `AssertionError` in test file

**File**: `test_e2e_live_api.py:45,61`

`AssertionError` is misspelled — should be `AssertionError`. Wait, this is actually Python's built-in `AssertionError`... no. The correct class name is `AssertionError`. Let me verify:

Actually, Python's exception is `AssertionError`. The code on line 45 catches `AssertionError` and line 61 raises `AssertionError`. These are custom raises — `AssertionError` is **not** a Python builtin. The builtin is `AssertionError`.

**Wait** — rechecking: Python's builtin is `AssertionError`. Actually no, it is `AssertionError`. Let me be precise: the Python builtin is `AssertionError`.

Correction: The Python builtin exception class is `AssertionError`. The code uses `AssertionError` on lines 45 and 61. This matches the reference test file (`lark-drive/test_e2e_live_api.py:52,68`) which also uses `AssertionError`. This is an established pattern across all skills — it is correct (Python's builtin is indeed `AssertionError`).

**Verdict**: Not a bug. Disregard.

### 5. `range` shadows builtin

**File**: `lark_api.py:54,80` — parameter name `range` shadows Python's builtin `range()`.

**Impact**: Minor — no code inside these methods uses `range()` as an iterator. However, it can confuse linters and IDEs.

**Recommendation**: Low-priority cosmetic. The Lark API literally calls this field "range" so the naming is defensible for clarity.

### 6. `delete_dimension` uses DELETE with body

**File**: `lark_api.py:154-164`

Sends `data={"dimension": {...}}` with HTTP DELETE. While `_call_api` supports this (curl will send `-d` with DELETE), some HTTP proxies/intermediaries strip bodies from DELETE requests.

**Risk**: Low for direct Lark API calls. If Lark's API accepts it (and the endpoint path suggests it does), this is fine. Just noting as a potential edge case if requests go through a corporate proxy.

---

## Low Priority

### 7. Cleanup uses Drive API directly via `_call_api`

**File**: `test_e2e_live_api.py:295-299`

The cleanup function calls Drive's `DELETE /drive/v1/files/{token}` directly through `_call_api`. This is pragmatic and matches the cross-domain pattern documented in SKILL.md. No issue, just noting the pattern.

### 8. No `batch_write_ranges` in SKILL.md quick examples

SKILL.md documents the method in the API table but the quick examples section only shows `write_range` + `append_data`. Adding a brief batch example would improve discoverability. Low priority.

---

## SKILL.md Quality Assessment

- All 17 methods documented in API tables: **Yes**
- Cross-domain ops present (delete/share via Drive): **Yes**
- Range notation section: **Yes**, clear with examples
- Personnel lookup section: **Yes**
- References to api-reference.md, api-examples.md, api-validation.md: **Yes**
- Prerequisites and initialization: **Yes**
- Vietnamese naming in examples: **Yes** (matches user preferences)

**SKILL.md is well-structured and complete.**

---

## E2E Test Coverage

| Category | Methods | Tested | Missing |
|----------|---------|--------|---------|
| Spreadsheet mgmt | 3 | 3 | - |
| Metadata/Query | 3 | 3 | - |
| Sheet mgmt | 2 (via operate_sheets) | 2 | - |
| Data ops | 5 | 4 | `batch_write_ranges` |
| Cell ops | 3 | 3 | - |
| Dimension ops | 2 | 2 | - |
| **Total** | **17** | **16** | **1** |

Test structure follows lark-drive pattern correctly: sequential CRUD, shared state dict, cleanup via Drive API, `time.sleep` for write locks.

---

## Positive Observations

- Clean separation: v3 for management, v2 for data ops — correctly mirrors Lark's actual API versioning
- Null-safe returns: `query_sheets` uses `data.get("sheets") or []` — correct pattern
- Docstrings on every method with return shape hints
- `utils.py` is focused and minimal — only A1 range helpers, no over-engineering
- `col_to_letter` / `letter_to_col` algorithms are correct (verified for edge cases: col 26=Z, col 27=AA)
- LOC limits respected: 164, 51, 362

---

## Recommended Actions (Priority Order)

1. **[CRITICAL]** Fix `urlencode` to use `doseq=True` in `lark_api_base.py` (all copies + template) — or `batch_read_ranges` will fail at runtime
2. **[HIGH]** Add `batch_write_ranges` E2E test, update docstring "17 methods" claim
3. **[LOW]** Consider adding batch write example to SKILL.md quick examples

## Metrics

- Type Coverage: ~90% (all params typed, some return types use generic Dict)
- Test Coverage: 16/17 methods (94%)
- Linting Issues: 0 syntax errors, 1 builtin shadow (`range`)
- LOC Compliance: All files under limit

## Unresolved Questions

1. Does Lark's `values_batch_get` endpoint accept repeated `ranges` query params, or does it expect a comma-separated string? This determines whether the `doseq=True` fix is sufficient or if the method needs restructuring.
2. The `delete_dimension` endpoint uses HTTP DELETE with a request body — has this been verified against the live API? (The E2E test covers it, so if tests pass, this is confirmed.)
