> **DEPRECATED**: This guide has been superseded by the `lark-skill-creator` dev tool at `.claude/skills/lark-skill-creator/`. Use `python3 .claude/skills/lark-skill-creator/scripts/scaffold-plugin.py` to create new skills. See `.claude/skills/lark-skill-creator/SKILL.md` for the updated workflow.

# Building Lark Skills

Guide for creating skills that interact with Lark/Feishu APIs using tokens from `lark-token-manager` MCP.

## Prerequisites

- `lark-token-manager` MCP server configured in `.mcp.json`
- API key hardcoded in `.mcp.json` (file is gitignored, safe for credentials)
- Target Lark app registered with appropriate scopes

## Quick Start (7 Steps)

### Step 1: Choose Domain & Scopes

Pick one Lark API domain. One skill per domain.

| Domain | API Version | Key Scopes |
|--------|-------------|------------|
| Calendar | v4 | `calendar:calendar`, `calendar:calendar:readonly` |
| Task | v2 | `task:task:read`, `task:task:write`, `task:tasklist:read`, `task:tasklist:write`, `task:section:read`, `task:section:write`, `task:custom_field:read`, `task:custom_field:write`, `task:comment:read`, `task:comment:write` |
| Contacts | v3 | `contact:contact`, `contact:contact.base:readonly`, `contact:contact:readonly_as_app`, `contact:user.base:readonly`, `contact:user.department:readonly`, `contact:user.email:readonly`, `contact:user.phone:readonly`, `contact:user.employee_id:readonly` |
| Base (Bitable) | v1 | `bitable:app` |
| Docs (DOCX) | v1 | `docx:document`, `docx:document.block:convert` |
| Drive | v1 | `drive:drive`, `drive:drive:readonly` |
| Sheets | v3 | `sheets:spreadsheet` |
| Messenger (IM) | v1 | `im:message`, `im:message:send_as_bot`, `im:message:send_multi_users`, `im:message:send_multi_depts`, `im:chat`, `im:chat:readonly`, `im:resource` |
| Approval | v4 | `approval:approval` |
| Attendance | v1 | `attendance:record:readonly` |
| Wiki | v2 | `wiki:wiki` |

### Step 2: Copy Template Files

```
skill-template/
├── SKILL.md.template           # Skill definition
├── plugin.json.template        # Plugin metadata
├── agent.md.template           # Dedicated subagent
├── .mcp.json.template          # MCP auto-config
├── api-reference.md.template   # Structured API docs
├── api-examples.md.template    # Code samples
├── api-validation.md.template  # Field constraints + error codes
└── scripts/
    ├── lark_api_base.py        # Shared base (copy as-is)
    └── lark_api.py.template    # Method stubs
```

Create your plugin directory:
```
plugins/lark-{domain}/
├── .claude-plugin/
│   └── plugin.json             # From template
├── .mcp.json                   # Auto-configures token manager MCP
├── agents/
│   └── lark-{domain}-agent.md  # Dedicated subagent
└── skills/lark-{domain}/
    ├── SKILL.md                 # From template
    ├── references/
    │   ├── api-reference.md     # Structured: required/optional, types, enums
    │   ├── api-examples.md      # Realistic code samples
    │   └── api-validation.md    # Field constraints + error codes
    └── scripts/
        ├── lark_api_base.py     # Copy from template (no changes)
        ├── lark_api.py          # Your domain client
        └── utils.py             # Domain-specific helpers
```

### Step 3: Implement lark_api.py

Extend `LarkAPIBase` with domain-specific methods.

```python
from lark_api_base import LarkAPIBase

class LarkDocsClient(LarkAPIBase):
    def create_document(self, title, folder_token=None):
        data = {"title": title}
        if folder_token:
            data["folder_token"] = folder_token
        return self._call_api("POST", "/docx/v1/documents", data=data)

    def list_blocks(self, document_id):
        return self._fetch_all(f"/docx/v1/documents/{document_id}/blocks")
```

**Key patterns:**
- Use `_call_api(method, endpoint, data, params)` for single requests
- Use `_fetch_all(endpoint, params)` for paginated lists
- Auto-retry on rate limits (code 1254290) with exponential backoff
- Token passed to `__init__` from MCP, never hardcoded

### Step 4: Write SKILL.md

Follow the template. Critical sections:
- **YAML frontmatter**: `name` and `description` drive auto-invocation. Include trigger words.
- **Prerequisites**: List exact scopes needed
- **Initialization**: 3-step MCP pattern (whoami -> get_token -> init client)
- **API Methods**: Table with 2-3 sentence descriptions and key param hints
- **Timestamp Rules**: Calendar=seconds (10 digits), Task=milliseconds (13 digits), others vary
- **Examples**: 2-3 practical examples with real code

Keep SKILL.md < 150 lines. Details go in `references/`.

### Step 4b: Structure API References (3-Layer Pattern)

Use progressive disclosure to balance token efficiency with API accuracy.

**Layer 1: SKILL.md** (always loaded by agent)
- Method signatures with 2-3 sentence descriptions and key param hints
- Quick examples for common operations
- Links to api-reference.md for full details

**Layer 2: api-reference.md** (loaded on-demand, ~300-400 lines)
- All methods with structured params table
- Mark each field: required/optional, type, constraints
- Key enum values (truncate to common ones)
- Return types and top error codes

Format per method:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|

**Layer 3: api-examples.md + api-validation.md** (loaded when needed)
- api-examples.md: 3-5 realistic code samples per method group
- api-validation.md: Full enum lists, nested schemas, all error codes

**Why**: AI reads SKILL.md for every invocation (~400 tokens). Only reads
api-reference.md when it needs field details (~900 tokens). Rarely needs
full validation rules. Total: ~1300 tokens typical vs ~2500+ if all inline.

**Source**: Extract from `lark-api-docs/{domain}/` official docs. Don't
copy prose — restructure into tables and concise format.

### Step 5: Create plugin.json

```json
{
  "name": "lark-{domain}",
  "description": "LarkSuite {domain} management - {brief}",
  "version": "1.0.0",
  "requires": ["lark-token-manager"],
  "skills": ["./skills/lark-{domain}"],
  "agents": ["./agents/lark-{domain}-agent.md"],
  "author": "YourName",
  "license": "proprietary"
}
```

`requires` declares dependency on `lark-token-manager`. `agents` lists the dedicated subagent.

### Step 5b: Add Agent and MCP Configuration

**Agent** (`agents/lark-{domain}-agent.md`):
- YAML frontmatter: name, description (with trigger words), tools, model, skills
- Body: capabilities list, workflow steps, important rules
- Tools: Bash, Read, Glob, Grep, WebFetch (no file editing)
- Model: `sonnet` for complex ops, `haiku` for simple queries
- Skills: preload own skill (SKILL.md injected at startup)

**MCP** (`.mcp.json` at plugin root):
- Auto-configures lark-token-manager when plugin is installed
- Uses `${ENV_VAR}` expansion for credentials
- Eliminates manual `.mcp.json` setup for users

### Step 6: Test with E2E Pattern

See [testing-patterns.md](./testing-patterns.md) for full guide.

```python
# Basic E2E test: create -> verify -> cleanup
resource = client.create_{resource}(test_data)
assert resource.get("guid") or resource.get("id")

fetched = client.get_{resource}(resource["guid"])
assert fetched["name"] == test_data["name"]

client.delete_{resource}(resource["guid"])
```

### Step 7: Register in Marketplace

Add entry to root `.claude-plugin/marketplace.json`:
```json
{
  "name": "lark-skills",
  "description": "LarkSuite skill ecosystem",
  "version": "1.0.0",
  "plugins": [
    {"name": "lark-{domain}", "path": "./plugins/lark-{domain}"}
  ]
}
```

## Token Selection Policy

**Prefer `user_access_token` over `tenant_access_token`** when the API supports both.

| Priority | Token | When to Use |
|----------|-------|-------------|
| 1st | `user_access_token` | API supports it — actions traceable to user, respects user permissions |
| 2nd | `tenant_access_token` | API requires it (e.g., IM send_message) OR no user context needed |

**Why user token first**: User tokens enable audit trails — Lark logs which user performed each action. Tenant tokens show "app" as actor, making it harder to trace who did what. User tokens also respect per-user permissions (e.g., folder access, doc visibility).

**When tenant token is required**: Some APIs only accept tenant token (e.g., `im/v1/messages` send). Check the [Token Type Matrix](https://open.larksuite.com/document/server-docs/api-call-guide/calling-process/overview) for each endpoint.

## Tenant Token Admin Policy (MANDATORY)

**Only org admins (`is_admin: true`) may acquire tenant tokens.** Each org typically has a single Lark app with broad permissions. Tenant tokens grant app-level access without per-user traceability, so unrestricted access is a security risk.

**Enforcement layers:**
1. **MCP server** (hard gate): `get_tenant_token` checks `is_org_admin` flag in DB. Non-admins get permission error.
2. **SKILL.md** (doc gate): Skills using tenant tokens MUST state "Org admin status required" in Prerequisites.
3. **Agent** (UX gate): Agent MUST check `whoami` → `is_admin` before calling `get_tenant_token`. If not admin, stop and inform user.

**Checklist for skills using tenant token:**
- [ ] SKILL.md Prerequisites: `**Org admin status** (enforced by MCP get_tenant_token)`
- [ ] SKILL.md description (YAML): mention "Org admins only"
- [ ] SKILL.md Step 1: `whoami` → verify `is_admin: true` before proceeding
- [ ] SKILL.md Step 2: `get_tenant_token(app_name)` (NOT `get_lark_token`)
- [ ] Agent.md workflow: admin check before token acquisition
- [ ] Agent.md rules: "Only org admins can use this skill" with error guidance

**Why this matters:** Each org has 1 shared app with permissions across all Lark APIs. Tenant token = app identity, not user identity. Without admin restriction, any member could act as the app — sending messages, reading contacts, modifying data — with no audit trail back to the individual.

## Token Acquisition Pattern

Every Lark skill MUST acquire tokens through the MCP server. Never hardcode tokens.

```
1. whoami() -> check is_admin status + linked_users[].tokens[].status
   - is_admin: true -> can use tenant token if needed
   - is_admin: false -> user token only (get_lark_token)
   - token "active" -> proceed
   - token "expired" -> refresh first
   - token missing -> need OAuth

2. Token selection:
   a. If API supports user_access_token (preferred):
      get_lark_token(app_name) -> { access_token, expires_at }
      - If expired: refresh_lark_token(app_name)
      - If refresh fails: start_oauth() -> present URL -> wait callback
   b. If API requires tenant_access_token only:
      Verify is_admin: true from Step 1
      get_tenant_token(app_name) -> { tenant_access_token, expire }
      - If not admin: STOP, inform user admin access required

3. Use token: Authorization: Bearer <access_token>
```

## Lark API Conventions

**Base URL:** `https://open.larksuite.com/open-apis/`

**Response format (all APIs):**
```json
{ "code": 0, "msg": "success", "data": { ... } }
```
`code: 0` = success. Non-zero = error. Never match on `msg` string.

**Pagination:**
```
Request: ?page_size=50&page_token=<token>
Response: { "items": [...], "has_more": true, "page_token": "..." }
```

**PATCH (partial update):**
```json
PATCH /task/v2/tasks/:guid
{ "task": { "summary": "New" }, "update_fields": ["summary"] }
```

**User ID types:** `?user_id_type=open_id|union_id|user_id`. Default: `open_id`.

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 99991663 | Token expired | Refresh via MCP |
| 99991664 | Permission denied | Check app scopes |
| 1254290 | Rate limited | Retry with backoff (2s, 4s, 8s) |

## Skill Design Principles

1. **Token-first**: Always acquire token before any API call. Prefer user token for traceability; use tenant token only when API requires it
2. **Admin-gated tenant token**: Skills using `tenant_access_token` MUST enforce org admin check (`whoami` → `is_admin`) and document it in Prerequisites, SKILL.md, and agent.md
3. **One domain per skill**: Calendar, Task, Base, etc. — never combine
4. **Progressive disclosure**: SKILL.md < 150 lines, details in references/
5. **Base module shared**: Copy `lark_api_base.py` as-is, never modify per-skill. Use `or {}` / `or []` pattern for null-safe Lark responses
6. **Pagination always**: Handle `has_more` for all list operations
7. **Auth via MCP only**: No embedded tokens, no direct OAuth flows
8. **3-layer references**: SKILL.md (overview) → api-reference.md (structured) → api-examples/validation (detail)
9. **Agent per plugin**: Focused context window, preloaded skill, restricted tools
10. **MCP auto-config**: Plugin-level `.mcp.json` with `${LARK_MCP_URL}` and `${LARK_SKILL_API_KEY}` env vars — never hardcode credentials

## Agent Guides (for Complex Domains)

- [Docs Block Fragmentation](./agent-guide-docs-blocks.md) — Content -> Lark Doc block tree
- [Base Records Import](./agent-guide-base-records.md) — CSV/JSON -> Bitable records
- [Testing Patterns](./testing-patterns.md) — E2E test structure and mocking

## Custom Skill Builder (Future)

A meta-skill that generates specialized Base skills from ERD/requirements. See the concept section at the bottom of [agent-guide-base-records.md](./agent-guide-base-records.md).
