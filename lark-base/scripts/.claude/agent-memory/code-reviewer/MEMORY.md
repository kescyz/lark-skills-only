# Code Reviewer Memory

## Project Patterns

### Lark Skill Plugin Structure
- Plugin root: `plugins/{skill-name}/`
- Structure: `.claude-plugin/plugin.json`, `agents/{name}-agent.md`, `skills/{name}/SKILL.md`, `skills/{name}/scripts/`, `skills/{name}/references/`
- Reference pattern: `plugins/lark-contacts/` (production, established)

### Lark API Client Pattern
- `lark_api_base.py`: Shared HTTP client (curl + subprocess), auto-retry, rate limit backoff (code 1254290), pagination via `_fetch_all`
- Domain modules inherit `LarkAPIBase`, router class uses multiple inheritance to compose
- MRO diamond is safe -- all converge to single `LarkAPIBase`
- `lark_api_base.py` is currently copy-pasted between skills (not shared)

### Known Code Quirks
- `cmd[4]` in `_call_api` is always the URL, even when data adds `-H`/`-d` after it (data appends, params mutates index 4)
- `if x:` truthiness checks in optional params prevent setting empty string/dict values (inherited from lark-contacts)
- `batch_create_tables` sends `fields: null` when fields not provided -- should conditionally include key

### Size Limits (enforced)
- Code files: < 200 LOC
- SKILL.md: < 150 lines
- api-reference.md: < 400 lines

### Review Checklist for Lark Skills
1. Method count matches claim (use MRO introspection)
2. Module LOC under 200
3. `lark_api_base.py` matches reference (identical copy)
4. Plugin JSON follows schema (name, description, version, requires, skills, agents, author, license)
5. No secrets in code (check token logging in tests)
6. Batch methods handle optional fields without sending null
7. E2E tests cover all methods or document skips
